# -*- coding: utf-8 -*-
"""
Attic Sorter

Created on Sat Aug  1 14:02:33 2020

@author: Zane Fadul
"""

import sqlite3
from tabulate import tabulate

#init db params
class Params:
    def __init__(self):
        self.TODOS = [(1,'Sell'), (2,'Donate'), (3,'Garbage'), (4,'Keep')]
        self.CONDITIONS = [(1,'Poor'), (2,'Fair'), (3,'Good'), (4,'Excellent')]
        self.TYPES = []

#setup sqlite3 db
def create_conn(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file,timeout=1)
    except Exception as e:
        print(e)
    finally:
        if conn:
            return conn, conn.cursor()
        
#check tables
def tables_exist(cursor):
    item_table = cursor.execute('''SELECT name 
                          FROM sqlite_master 
                          WHERE type='table'
                          AND name="items"''').fetchall()
    if len(item_table) == 1:
        return True
    return False

#init tables
def create_tables(conn, cursor, params):
    #init todos table
    cursor.execute('''CREATE TABLE IF NOT EXISTS todos (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL)''')
    for TODO in params.TODOS:
        cursor.execute(f'''INSERT INTO todos VALUES ({TODO[0]},"{TODO[1]}")''')
        
    #init types table
    cursor.execute('''CREATE TABLE IF NOT EXISTS types (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL)''')
    
    #init conditions table
    cursor.execute('''CREATE TABLE IF NOT EXISTS conditions (
                        id INTEGER PRIMARY KEY,
                        condition TEXT NOT NULL)''')
    for CONDITION in params.CONDITIONS:
        cursor.execute(f'''INSERT INTO conditions VALUES ({CONDITION[0]},"{CONDITION[1]}")''')
    


    #init items table
    cursor.execute('''CREATE TABLE IF NOT EXISTS items (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        desc TEXT,
                        todo_key INTEGER NOT NULL,
                        type_key INTEGER NOT NULL,
                        cond_key INTEGER NOT NULL,
                        FOREIGN KEY (todo_key) REFERENCES todos (id)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE,
                        FOREIGN KEY (type_key) REFERENCES types (id)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE,
                        FOREIGN KEY (cond_key) REFERENCES conditions (id)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE
                        )''')
    
    conn.commit()

#setup user Interface
class Interface:
    
    def __init__(self, cursor, params):
        self.cursor = cursor
        self.params = params
        self.STATES = ['EXIT','MENU','ADD','TYPE']
        self.COMMANDS = ['e','a','t']
        self.state = 'MENU'
        
    def interpretInput(self, userInput):
        if self.state == 'MENU':
            if userInput == 'e':
                self.state = 'EXIT'
            elif userInput == 'a':
                self.state = 'ADD'
            elif userInput == 't':
                self.state = 'TYPE'
        elif self.state == 'ADD' or self.state == 'TYPE':
            if userInput == 'e':
                self.state = 'MENU'
        else:
            return
    
    def displayAddFeature(self, userInput):
        class notEnoughProps(Exception): pass
        print('LOG A NEW ITEM (name, desc, todo, type, condition)\n')
        try:
            newItemProps = userInput.split(' ')
            if len(newItemProps) < 5:
                raise notEnoughProps
            output = self.cursor.execute(f'INSERT INTO items VALUES ({newItemProps[0]},{newItemProps[1]},{newItemProps[2]},{newItemProps[3]},{newItemProps[4]})')
            print(output)
        except notEnoughProps:
            print("You didnt put in enough info")
    
    def displayTypeFeature(self, userInput):
        print('ADD A NEW TYPE (min 3 characters)\n')
        print(tabulate(self.params.TYPES,headers=('TYPE CODES:',)))
        if userInput is None or len(userInput) <= 3 or userInput in self.params.TYPES:
            return
        self.cursor.execute(f'INSERT INTO types (name) VALUES ("{userInput}")')
        print(f'Added {userInput}')
        
    def run(self):
        #Event Loop
        while self.state != 'EXIT':
            userInput = input('>')
            self.interpretInput(userInput)
            if self.state == 'ADD':
                self.displayAddFeature(userInput)
            elif self.state == 'TYPE':
                self.params.TYPES = (self.cursor.execute('SELECT * FROM types').fetchall())
                self.displayTypeFeature(userInput)
        print('Bye-bye')
    

if __name__ == '__main__':
    conn, cursor = create_conn('attic.db')
    params = Params()
    try:
        if not tables_exist(cursor):
            create_tables(conn, cursor, params)
        interface = Interface(cursor, params)
        interface.run()
    except Exception as e:
        print(e)
    finally:
        conn.commit()
        conn.close()