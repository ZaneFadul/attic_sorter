# -*- coding: utf-8 -*-
"""
Attic Sorter

Created on Sat Aug  1 14:02:33 2020

@author: Zane Fadul
"""
import time
import os
import sqlite3
import xlsxwriter

from tabulate import tabulate

def clearScreen():
    try:
        os.system('cls')
    except:
        os.system('clear')
    finally:
        pass
    
#==============================================================init db params
class Params:
    def __init__(self, DB_Name):
        self.TODOS = [(1,'Sell'), (2,'Donate'), (3,'Garbage'), (4,'Keep')]
        self.CONDITIONS = [(1,'Poor'), (2,'Fair'), (3,'Good'), (4,'Excellent')]
        self.TYPES = []
        self.NAME = DB_Name

#==============================================================setup user Interface
class Interface:
    
    def __init__(self, cursor, params):
        self.cursor = cursor
        self.params = params
        self.params.TYPES = (self.cursor.execute('SELECT * FROM types').fetchall())
        self.STATES = ['EXIT','MENU','ADD','TYPE']
        self.COMMANDS = ['e','a','t','d','x']
        self.state = 'MENU'
        
    def interpretInput(self, userInput):
        if userInput == 'ls':
            print(self.state)
            return
        if self.state == 'MENU':
            if userInput == 'e':
                self.state = 'EXIT'
            elif userInput == 'a':
                self.state = 'ADD'
            elif userInput == 't':
                self.state = 'TYPE'
            elif userInput == 'd':
                self.displayItems()
            elif userInput == 'x':
                self.exportCSV()
        elif self.state == 'ADD' or self.state == 'TYPE':
            if userInput == 'e':
                self.state = 'MENU'
        else:
            print('Unknown Command')
    
    def getReadableItems(self):
        self.params.TYPES = (self.cursor.execute('SELECT * FROM types').fetchall())
        allItems = self.cursor.execute('SELECT * FROM items').fetchall()
        for i in range(len(allItems)):
            allItems[i] = list(allItems[i])
            allItems[i][3] = self.params.TYPES[allItems[i][3] - 1][1]
            allItems[i][4] = self.params.TODOS[allItems[i][4] - 1][1]
            allItems[i][5] = self.params.CONDITIONS[allItems[i][5] - 1][1]
        return allItems
    
    def displayAddFeature(self, userInput):
        class notEnoughProps(Exception): pass
        print('LOG A NEW ITEM (name, desc, type, todo_key, condition)\n')
        table_type = tabulate(self.params.TYPES, headers=['Key', 'Type'])
        table_todo = tabulate(self.params.TODOS, headers=['Key', 'To-Do'])
        table_conditions = tabulate(self.params.CONDITIONS, headers=['Key','Condition'])
        print(table_type+'\n\n', table_todo+'\n\n', table_conditions)
        #print(tabulate([self.params.TODOS,self.params.CONDITIONS,self.params.TYPES],headers=['To-Do Keys','Condition Keys','Type Keys']))
        
        try:
            newItemProps = userInput.split(',')
            for item in range(len(newItemProps)):
                newItemProps[item] = newItemProps[item].strip()
            if len(newItemProps) < 5:
                raise notEnoughProps
            self.cursor.execute(f'INSERT INTO items(name, desc, type_key, todo_key, cond_key) VALUES ("{newItemProps[0]}","{newItemProps[1]}",{int(newItemProps[2])},{int(newItemProps[3])},{int(newItemProps[4])})')
            print(f'Successfully added {newItemProps[0]}')
        except notEnoughProps:
            print('You didnt put in enough info')
    
    def displayTypeFeature(self, userInput):
        self.params.TYPES = (self.cursor.execute('SELECT * FROM types').fetchall())
        print('ADD A NEW TYPE (min 3 characters)\n')
        print(tabulate(self.params.TYPES,headers=('TYPE CODES:',)))
        if userInput is None or len(userInput) <= 3 or userInput in self.params.TYPES:
            return
        userInput = userInput.lower()
        userInput = userInput.capitalize()
        self.cursor.execute(f'INSERT INTO types (name) VALUES ("{userInput}")')
        print(f'Added {userInput}')
        
    def displayItems(self):
        allItems = self.getReadableItems()
        print(tabulate(allItems,headers=['ID','Name','Description','Item Type','To Do', 'Condition']))
    
    def exportCSV(self):
        try:
            workbook = xlsxwriter.Workbook(f'{self.params.NAME}.xlsx')
            sheet_all = workbook.add_worksheet('All')
            todo_sheets = []
            cell_orange = workbook.add_format({'bg_color': 'orange'})
            cell_blue = workbook.add_format({'bg_color': 'blue'})
            cell_red = workbook.add_format({'bg_color': 'red'})
            cell_green = workbook.add_format({'bg_color': 'green'})
            todo_colors = {'Sell':cell_orange,
                           'Donate':cell_blue,
                           'Garbage':cell_red,
                           'Keep':cell_green,
                           }
            for todo in self.params.TODOS:
                todo_sheets.append((todo[0], workbook.add_worksheet(f'{todo[1]}')))
            for i, item in enumerate(self.getReadableItems()):
                cell_format = todo_colors[item[4]] #todo
                for col in range(len(item)-1):
                    sheet_all.write(i,col,item[col+1], cell_format)
            workbook.close()
        except:
            return
        
    def run(self):
        userInput = None
        #Event Loop
        while self.state != 'EXIT':
            self.params.TYPES = (self.cursor.execute('SELECT * FROM types').fetchall())
            if self.state == 'ADD':
                self.displayAddFeature(userInput)
            elif self.state == 'TYPE':
                self.displayTypeFeature(userInput)
            userInput = input('>')
            self.interpretInput(userInput)
        print('Bye-bye')
    
#==============================================================setup sqlite3 db
def create_conn(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file,timeout=1)
    except Exception as e:
        print(e)
    finally:
        if conn:
            return conn, conn.cursor()
        
#==============================================================check tables
def tables_exist(cursor):
    item_table = cursor.execute('''SELECT name 
                          FROM sqlite_master 
                          WHERE type='table'
                          AND name="items"''').fetchall()
    if len(item_table) == 1:
        return True
    return False

#==============================================================init tables
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
                        type_key INTEGER NOT NULL,
                        todo_key INTEGER NOT NULL,
                        cond_key INTEGER NOT NULL,
                        FOREIGN KEY (type_key) REFERENCES types (id)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE,
                        FOREIGN KEY (todo_key) REFERENCES todos (id)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE,
                        FOREIGN KEY (cond_key) REFERENCES conditions (id)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE
                        )''')
    
    conn.commit()

#==============================================================main
if __name__ == '__main__':
    database = ''
    illegalFSNameChars = [':','.','"', '/','\'','^','@','!','?']
    while len(database) <= 0:
        database = input('Name of Declutter Database: ')
        for char in illegalFSNameChars:
            if char in database:
                database = ''
    conn, cursor = create_conn(f'{database}.db')
    params = Params(database)
    clearScreen()
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
        time.sleep(.8)