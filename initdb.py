#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import sqlite3
import os
import sys
from colorama import Fore
from colorama import init as initcolor
from time import sleep

def initiate(dbfile):    
    connection = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE messages (                      
                      message_id INTEGER PRIMARY KEY,
                      username TEXT,
                      dt TIMESTAMP,                 
                      txt TEXT,
                      FOREIGN KEY(username) REFERENCES users (username)
                      )''') 
    #dt == timestamp
    #txt == message.text
    # FOREIGN KEY (key in this table) REFERENCES users (key in foreign table)
    # ↑ to create releationships
    cursor.execute('''CREATE TABLE tickets (                      
                      ticket_id INTEGER PRIMARY KEY,
                      status TEXT,
                      message_id INTEGER,
                      FOREIGN KEY(message_id) REFERENCES messages (message_id)
                      )''')
    cursor.execute('''CREATE TABLE users (                      
                      username TEXT PRIMARY KEY,
                      firstname TEXT,
                      lastname TEXT,
                      admin_rights BOOLEAN
                      )''')
    cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', ('xtipacko',  'Евгений', 'Вотэва', True))
    
    connection.commit()
    connection.close()

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', color=Fore.WHITE):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{color}{bar}{Fore.RESET}| {percent}% {suffix}', end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

def main():
    initcolor()
    dbfile = 'rt.bisv.bot.db'
    answ = input(f'Are you sure you want to initiate SQL Lite database: {dbfile}? [Y/n]: ')
    if answ == 'Y' or answ == 'y':
        print(f'{Fore.YELLOW}ATENTION! Script will erase existing database, and create new form scratch{Fore.RESET}')
        print('You can still stop the process, press Ctrl+C\n')
        # set timer
        wait_timer = 5*10
        # Initial call to print 0% progress
        printProgressBar(0, wait_timer, prefix = 'Progress:', 
                         suffix = 'Waiting', length = 50, color=Fore.CYAN)
        for i, item in enumerate(range(0, wait_timer+1)):
            # Do stuff...
            sleep(0.1)
            # Update Progress Bar
            printProgressBar(i, wait_timer, prefix = 'Progress:', 
                             suffix = 'Waiting', length = 50, color=Fore.CYAN)

        print('Start.')
        if os.path.isfile(dbfile):
            os.remove(dbfile)
            print('Database erased.')
        else:
            print('Nothing needs to be erased.')
            
        initiate(dbfile)
        print(f'{Fore.YELLOW}Database successfully created.{Fore.RESET}')
        input('Press any key to exit')
    else:
        print('Canceled')

if __name__ == '__main__':
    main()

