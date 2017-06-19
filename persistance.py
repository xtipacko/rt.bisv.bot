#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import sqlite3
from copy import deepcopy
from datetime import datetime
TICKET_STATUS = {'created', 'active', 'solved'}


class BOTPersistance():


    def __init__(self, dbfile):
        self.dbfile = dbfile        
        

    def __connect_db(self):
        self.connection = sqlite3.connect(self.dbfile, detect_types=sqlite3.PARSE_DECLTYPES) 
        # detect_types - for date-time timestamps
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()


    def __close_db(self):
        if self.connection:
            self.connection.close()


    def add_message(self, message_id=None, username=None, dt=None, txt=None):        
        #dt == datetime field, txt == message text field
        if not all((message_id, username, dt, txt)):
            #raise ValueError('Not all parameters filled')
            return       
        self.__connect_db()
        self.cursor.execute('REPLACE INTO messages VALUES (?, ?, ?, ?)',
                            (message_id, username, dt, txt))
        self.connection.commit()
        self.__close_db()


    def del_message(self, message_id):
        pass


    def del_messages(self, status=None, after_ts=None, before_ts=None):
        pass


    def is_ticket(self, ticket_id):
        self.__connect_db()
        self.cursor.execute('SELECT 1 FROM tickets WHERE ticket_id = ?', (ticket_id, ))
        if len(self.cursor.fetchall()) >= 1:
            self.__close_db()
            return True
        else:
            self.__close_db()
            return False
        


    def add_ticket(self, ticket_id=None, status=None, message_id=None):
        if not all((ticket_id, status, message_id)):            
            #raise ValueError('Not all parameters filled')
            return
        if self.is_ticket(ticket_id):
            # log attempt to write to existing ticket
            return
        self.__connect_db()
        self.cursor.execute('INSERT INTO tickets VALUES (?, ?, ?)',
                            (ticket_id, status, message_id))
        self.connection.commit()
        self.__close_db()


    def del_ticket(self, ticket_id):        
        #existance check
        if not self.is_ticket(ticket_id):
            # log attempt to delete nonexisting ticket
            return
        self.__connect_db()
        self.cursor.execute('DELETE FROM tickets WHERE ticket_id = ?', (ticket_id, ))
        self.connection.commit()
        self.__close_db()


    def change_ticket_status(self, ticket_id, status=None):        
        if not self.is_ticket(ticket_id):
            # log attempt to change nonexisting ticket
            return
        if status not in TICKET_STATUS:
            # log attempt to set invalid status
            return
        self.__connect_db()
        self.cursor.execute('UPDATE tickets SET status = ? WHERE ticket_id = ?', (status, ticket_id))
        self.connection.commit()
        self.__close_db()

    
    def add_user(self, username=None, firstname=None, lastname=None, admin_rights=False):        
        #admin_rights is False by default
        if not all((username, firstname, lastname)):
            #raise ValueError('Not all parameters filled')
            return
        self.__connect_db()
        self.cursor.execute('REPLACE INTO users VALUES (?, ?, ?, ?)',
                            (username, firstname, lastname, admin_rights))
        self.connection.commit()
        self.__close_db()

    
    def is_user(self, username):
        self.__connect_db()
        self.cursor.execute('SELECT 1 FROM users WHERE username = ?', (username, ))
        result = len(self.cursor.fetchall()) >= 1
        self.__close_db()
        return result
        

    
    def change_user_rights(self, username=None, admin_rights=False):        
        if not username:
            #raise ValueError('Not all parameters filled')
            return      
        user_exist = self.is_user(username)
        if user_exist:
            self.__connect_db()
            # User found in DB
            admin_rights = int(admin_rights)
            self.cursor.execute('UPDATE users SET admin_rights = ? WHERE username = ?', 
                                (admin_rights, username))
            self.connection.commit()
            self.__close_db()
        else:
            # User not found in DB
            # log unsuccessful attempt to find user
            return



    def get_user_info(self, username):
        # If user doesn't exist, returns None
        self.__connect_db()
        self.cursor.execute('SELECT firstname, lastname, admin_rights FROM users WHERE username = ?', (username, ))
        firstname, lastname, admin_rights = self.cursor.fetchone()
        admin_rights = bool(admin_rights)
        self.__close_db()
        return { 'firstname'   : firstname, 
                 'lastname'    : lastname,
                 'admin_rights': admin_rights }
    

    def is_admin(self, username):
        # If user doesn't exist, he has no rights, returns False
        self.__connect_db()
        self.cursor.execute('SELECT admin_rights FROM users WHERE username = ?', (username, ))
        retrieved = self.cursor.fetchone()
        self.__close_db()
        if retrieved:
            admin_rights = bool(retrieved[0])
            return admin_rights
        else:
            return False


    def get_tickets(self, status=None, after_ts=None, before_ts=None, inverse=False):
        if status not in TICKET_STATUS and status != None:
            return
        if status == None:
            status = '%'
        #TO-DO Use less hacky approach
        shim = ''
        if inverse:
            NOTshim = 'NOT' #dirty hack            
            after_ts, before_ts = before_ts, after_ts #even more dirty hack  
        if after_ts == None:
            after_ts = datetime.min
        if before_ts == None:
            before_ts = datetime.max
        self.__connect_db()
        self.cursor.execute(f'''SELECT t.ticket_id, 
                                       t.status, 
                                       m.username, 
                                       u.firstname, 
                                       u.lastname, 
                                       m.dt, 
                                       m.txt
                                FROM tickets t 
                                NATURAL JOIN messages m
                                LEFT JOIN users u ON m.username = u.username
                                WHERE t.status {NOTshim} LIKE ? 
                                AND m.dt BETWEEN ? AND ?''', (status, after_ts, before_ts))
        rows = self.cursor.fetchall()
        self.__close_db()
        result = [ dict(row) for row in rows ]
        return result

    
    def get_ticket(self, ticket_id):
        self.__connect_db()
        self.cursor.execute('''SELECT t.ticket_id, 
                                      t.status, 
                                      m.username, 
                                      u.firstname, 
                                      u.lastname, 
                                      m.dt, 
                                      m.txt
                               FROM tickets t 
                               NATURAL JOIN messages m
                               LEFT JOIN users u ON m.username = u.username
                               WHERE t.ticket_id = ?''', 
                            (ticket_id, ))
        ticket_data = self.cursor.fetchone()
        self.__close_db()
        if ticket_data:
            return dict(ticket_data)
        else:
            return



    def close(self):
        pass
