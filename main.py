#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
import logging
from telegram.ext import Updater
from handlers import BotHandler
from params import TOKEN, SERVER_IP, PORT, CERT, KEY

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def main():
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    bothandler = BotHandler('rt.bisv.bot.db')
    #Регистрируем call-back-и в dispatcher-е
    for handler in bothandler.all_handlers:
        dispatcher.add_handler(handler)    
    try:
        updater.start_webhook(listen   =  SERVER_IP,
                              port     =  PORT,
                              url_path =  TOKEN,
                              key      =  KEY,
                              cert     =  CERT,
                              webhook_url=f'https://{SERVER_IP}:{PORT!s}/{TOKEN}')
    except:
        #to-do: write trace to log file
        pass
    finally:
        bothandler.close()
        #to-do: close, and clean...



if __name__ == '__main__':
    main()