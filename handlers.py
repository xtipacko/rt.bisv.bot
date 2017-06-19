#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from persistance import BOTPersistance
from equiv_map import TICKET_STATUS, STATUS_REPORTS
import re

reTicket = re.compile(r'[0-9]{5,}')

class BotHandler:
    def __init__(self, dbfile):        
        self.db = BOTPersistance(dbfile)
        self.all_handlers = [ CommandHandler('start',       self.start),
                              CommandHandler('rm',          self.rm, pass_args=True),
                              CommandHandler('add_user',    self.add_user, pass_args=True),
                              CommandHandler('authorize',   self.authorize, pass_args=True), # Чтоб добавить админа
                              CommandHandler('deauthorize', self.deauthorize, pass_args=True), # Чтоб отобрать права админа
                              CommandHandler('shutdown',    self.shutdown), 
                              CommandHandler('silence',     self.silence), 
                              CommandHandler('unsilence',   self.unsilence), 
                              CommandHandler('list',        self.lst),
                              CommandHandler('list_all',    self.lst_all),
                              CommandHandler('show',        self.show, pass_args=True),
                              MessageHandler(Filters.text,  self.msg_handler),
                              MessageHandler(Filters.photo, self.img_handler),
                              MessageHandler(Filters.all,   self.new_member) ] # check if there is smth better 
        self.silencemode = False


    def __tickets_f_msg(self, msg):
        '''returns list of tickets in message'''
        return re.findall(reTicket, msg)
            
        
    def __status_f_msg(self, msg):
        for key in STATUS_REPORTS.keys():        	
            for val in STATUS_REPORTS[key]:
                if val in msg:
                    return key
        return 'created'
        
        
    def msg_handler(self, bot, update):
        msg_written = False
        #Собираем всё, чтоб удобненько
        username   = update.message.from_user.username
        firstname  = update.message.from_user.first_name
        lastname   = update.message.from_user.last_name
        message_id = update.message.message_id
        timestamp  = update.message.date    
        txt        = update.message.text
    
        #Если пользователь не в базе - то добавляем
        if not self.db.is_user(username):
            self.db.add_user(username=username,
                             firstname=firstname,
                             lastname=lastname)
    
        #Разбираемся, что в сообщении
        ticket_lst = self.__tickets_f_msg(txt)
        status = self.__status_f_msg(txt)
    
        #Проверяем не является ли это сообщение ответом на другое    
        is_reply = False
        if update.message.reply_to_message:
            is_reply = True
            orig_msg = update.message.reply_to_message
            orig_tickets = self.__tickets_f_msg(orig_msg.text)  
            #Если это ответ, то для обработки более приоритетен список заявок в ответе.
            #Но только, если они там есть, 
            #в противном случае перезапишем их на список из оригинального сообщения
            if not ticket_lst:
                ticket_lst = orig_tickets
        #Если ни в исходном, ни в ответном сообщении нет тикетов, можно гулять
        if not ticket_lst:
            return  
        #Иначе двигаемся дальше и проверяем, если это изначальное сообщение, 
        #и у нас нет тикетов из него, то добавляем его и тикеты в базу ... 
        #Проверяем, существуют ли тикеты в базе, если хотябы один нет,
        #то добавляем туда сообщение один раз и все не существующие тикеты присваиваем к этому сообщению
        for ticket in ticket_lst:
            if not self.db.is_ticket(ticket):
                if not msg_written:
                    self.db.add_message(message_id=message_id,
                                       username=username,
                                       dt=timestamp,
                                       txt=txt)
                    msg_written = True
                self.db.add_ticket(ticket_id=ticket,
                                  status=status,
                                  message_id=message_id)
            #Если тикет уже в базе, меняем его статус, только если пользователь имеет админские права
            else:
                if self.db.is_admin(username):
                    self.db.change_ticket_status(ticket, status=status)
        
        
    def new_member(self, bot, update):
        pass
    
    
    def img_handler(self, bot, update):
        pass
        
        
    def start(self, bot, update):
        msg =  ('Я бот для учета заявок.\n'
                'Использую любую последовательность чисел длиннее 5 в сообщении, '
                'в качестве идентификатора заявки (номер заявки, либо номер договора), '
                'и в последующем отслеживаю статус выполнения заявки.')
        bot.send_message(chat_id=update.message.chat_id, text=msg)
        
        
    def rm(self, bot, update, args):
        #args - Содержат аргументы переданные через команду
        #проверяем авторизацию по юзернейму      
        if len(args) < 1:
            bot.send_message(chat_id=update.message.chat_id, text='Укажите номера заявок, которые нужно удалять!')
            return      
        if self.db.is_admin(update.message.from_user.username):
            #log it
            # TO-DO: if message doesn't have any other tickets, also remove it 
            for ticket_id in args:
                #TO-DO: message_id = self.db.get_ticket(ticket_id)
                self.db.del_ticket(ticket_id)
                #TO-DO: if not self.db.get_tickets(message_id=message_id):
                #TO-DO:     self.db.del_message(message_id)      
            bot.send_message(chat_id=update.message.chat_id, text=f'Заявки {", ".join(args)} успешно удалены.')
        else:
            bot.send_message(chat_id=update.message.chat_id, text='Функция удаления заявок доступна только админам.')
    
    
    def lst(self, bot, update):
        result = self.db.get_tickets(status='solved', inverse=True)
        msg = ''
        ticket_descriptions = []
        for ticket in result:
            # TO-DO Simplify it
            timestamp = ticket['dt'].strftime('%d.%m.%Y %H:%M')
            ticket_descriptions.append(f'{ticket["ticket_id"]}, {ticket["status"]}\n'
                                       f'  [{timestamp}]: {ticket["firstname"]} {ticket["lastname"]} ({ticket["username"]}), ')
        if result:
            msg = '\n'.join(ticket_descriptions)
        else:
            msg = 'В Базе нет невыполненных заявок'
        bot.send_message(chat_id=update.message.chat_id, text=msg)
    
    
    def lst_all(self, bot, update):
        result = self.db.get_tickets(status='solved', inverse=True)
        msg = ''
        ticket_descriptions = []
        for ticket in result:
            # TO-DO Simplify it
            timestamp = ticket['dt'].strftime('%d.%m.%Y %H:%M')
            ticket_descriptions.append(f'{ticket["ticket_id"]}, {ticket["status"]}\n'
                                       f'  [{timestamp}]: {ticket["firstname"]} {ticket["lastname"]} ({ticket["username"]}), ')
        if result:
            msg = '\n'.join(ticket_descriptions)
        else:
            msg = 'Не могу найти ни одной заявки в базе \xF0\x9F\x98\xB1'
        bot.send_message(chat_id=update.message.chat_id, text=msg)
  

    def show(self, bot, update, args):
        if len(args) < 1:
            bot.send_message(chat_id=update.message.chat_id, text='Че показывать то? Номер заявки укажи!')
            return
        ticket = self.db.get_ticket(args[0]) # Воспринимает только одну заявку - первую
        msg = ''
        if ticket:
            timestamp = ticket['dt'].strftime('%d.%m.%Y %H:%M')
            msg = (f'{ticket["ticket_id"]}, {ticket["status"]}\n'
                   f'[{timestamp}]: {ticket["firstname"]} {ticket["lastname"]} ({ticket["username"]})\n'
                    'Сообщение:\n'
                   f'{ticket["txt"]}')
        else:
            msg = f'Заявка {args[0]} не найдена в БД'
        bot.send_message(chat_id=update.message.chat_id, text=msg)
    
    
    def authorize(self, bot, update, args):
        if len(args) < 1:
            bot.send_message(chat_id=update.message.chat_id, text='Кого авторизовать? Юзернеём сюда!')
            return
        username = args[0]
        if self.db.is_admin(update.message.from_user.username):
            if self.db.is_user(username):
                self.db.change_user_rights(username=username, admin_rights=True)
            else:
                bot.send_message(chat_id=update.message.chat_id, text=f'Пользователь {username} отсутствует в БД')
        else:
            bot.send_message(chat_id=update.message.chat_id, text='У Вас нет прав на эту операцию')


    def deauthorize(self, bot, update, args):
        if len(args) < 1:
            bot.send_message(chat_id=update.message.chat_id, text='Кого деавторизовать? Юзернейм в студию!')
            return
        username = args[0]
        if self.db.is_admin(update.message.from_user.username):
            if self.db.is_user(username):
                self.db.change_user_rights(username=username, admin_rights=False)
            else:
                bot.send_message(chat_id=update.message.chat_id, text=f'Пользователь {username} отсутствует в БД')
        else:
            bot.send_message(chat_id=update.message.chat_id, text='У Вас нет прав на эту операцию')
    

    def add_user(self, bot, update, args):
        if len(args) < 3:
            bot.send_message(chat_id=update.message.chat_id, text='Необходимо последовательно указать: username Имя Фамилия!')
            return
        username, firstname, lastname  = args[0:3]
        if self.db.is_admin(update.message.from_user.username):            
            self.db.add_user(self, username=username, firstname=firstname, lastname=lastname)
            # TO-DO: check if everything is OK
            bot.send_message(chat_id=update.message.chat_id, 
                             text=f'Пользователь {username} ({lastname} {firstname}) добавлен в БД')
        else:
            bot.send_message(chat_id=update.message.chat_id, text='У Вас нет прав на эту операцию')
    
    
    def shutdown(self, bot, update):
        # проверить авторизацию
        bot.send_message(chat_id=update.message.chat_id, text='Полное отключение бота не реализованно')
    
    
    def silence(self, bot, update):
        # проверить авторизацию
        bot.send_message(chat_id=update.message.chat_id, text='Режим тишины не реализован')
    
    
    def unsilence(self, bot, update):
        # проверить авторизацию
        bot.send_message(chat_id=update.message.chat_id, text='Отключение режима тишины не реализовано')


    def close(self):
        self.db.close()

