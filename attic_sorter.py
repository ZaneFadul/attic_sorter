# -*- coding: utf-8 -*-
"""
Attic Sorter

Created on Sat Aug  1 14:02:33 2020

@author: Zane Fadul
"""
import time
import os
import subprocess

try:
    import xlsxwriter
except:
    try:
        subprocess.check_call(['py','-m','pip','install','xlsxwriter'])
        import xlsxwriter
    except:
        print('Cannot install module.')
        time.sleep(0.5)
        raise Exception
try:
    import sqlite3
except:
    try:
        subprocess.check_call(['py','-m','pip','install','sqlite3'])
        import sqlite3
    except:
        print('Cannot install module.')
        time.sleep(0.5)
        raise Exception  

try:
    from tabulate import tabulate
except:
    try:
        subprocess.check_call(['py','-m','pip','install','tabulate'])
        from tabulate import tabulate
    except:
        print('Cannot install module.')
        time.sleep(0.5)
        raise Exception  

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
        self.EXIT = 'e'
        self.MENU = 'm'
        self.ADD = 'a'
        self.TYPE = 't'
        self.EXPORT = 'x'
        self.DISPLAY = 'd'
        self.UPDATE = 'u'
        self.STATES = [self.MENU,self.ADD,self.TYPE,self.UPDATE]
        self.state = 'MENU'
        self.COMMANDS = None
        self.generateCommands()
        self.HISTORY = []
    
    def generateCommands(self):
        self.COMMANDS = [(self.EXIT,f'exit from {self.state}'),
                 (self.ADD,'log a new item'),
                 (self.TYPE,'add a new item type'),
                 (self.EXPORT,'export as excel sheet'),
                 (self.DISPLAY,'display all logged items'),
                 (self.UPDATE,'update logged items')
                 ]
        
    def interpretInput(self, userInput):
        if self.state == 'MENU':
            if userInput == self.EXIT:
                self.state = 'EXIT'
            elif userInput == self.ADD:
                self.updateTypes()
                self.state = 'ADD'
            elif userInput == self.TYPE:
                self.updateTypes()
                self.state = 'TYPE'
            elif userInput == self.DISPLAY:
                self.displayItems()
            elif userInput == self.EXPORT:
                self.exportCSV()
            elif userInput == self.UPDATE:
                self.state = 'UPDATE'
        elif self.state == 'ADD' or self.state == 'TYPE' or self.state == 'UPDATE':
            if userInput == 'e':
                self.state = 'MENU'
        else:
            print('Unknown Command')
    
    def updateTypes(self):
        self.params.TYPES = (self.cursor.execute('SELECT * FROM types').fetchall())
        
    def displayCommands(self):
        self.generateCommands()
        table = tabulate(self.COMMANDS)
        print(f'COMMANDS\n {table}\n')
        
    def getReadableItems(self):
        self.updateTypes()
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
            
            #error handle type
            if not newItemProps[2].isdigit() or int(newItemProps[2]) not in range(1, len(self.params.TYPES) + 1):
                print('invalid type #')
                return
            #error handle todo
            if not newItemProps[3].isdigit() or int(newItemProps[3]) not in range(1, len(self.params.TODOS) + 1):
                print('invalid todo #')
                return
            #error handle condition
            if not newItemProps[4].isdigit() or int(newItemProps[4]) not in range(1, len(self.params.CONDITIONS) + 1):
                print('invalid cond #')
                return
            
            self.cursor.execute(f'INSERT INTO items(name, desc, type_key, todo_key, cond_key) VALUES ("{newItemProps[0]}","{newItemProps[1]}",{int(newItemProps[2])},{int(newItemProps[3])},{int(newItemProps[4])})')
            print(f'Successfully added {newItemProps[0]}')
        except notEnoughProps:
            print('You didnt put in enough info')
    
    def displayTypeFeature(self, userInput):
        self.updateTypes()
        print('ADD A NEW TYPE (min 3 characters)\n')
        print(tabulate(self.params.TYPES,headers=('TYPE CODES:',)))
        if userInput is None or len(userInput) < 3 or userInput in self.params.TYPES:
            print('INVALID INPUT')
            return
        userInput = userInput.lower()
        userInput = userInput.capitalize()
        self.cursor.execute(f'INSERT INTO types (name) VALUES ("{userInput}")')
        print(f'Added {userInput}')
        
    def displayItems(self):
        allItems = self.getReadableItems()
        print(tabulate(allItems,headers=['ID','Name','Description','Item Type','To Do', 'Condition']))
    
    def displayUpdateFeature(self, userInput):
        if not userInput.isdigit():
            print('Input a valid Item ID #')
            return
        ID = int(userInput)
        currentItem = self.cursor.execute(f'SELECT * FROM items WHERE ID = "{ID}"').fetchall()
        print(currentItem)
    
    def exportCSV(self):
        try:
            allItems = self.getReadableItems()
            workbook = xlsxwriter.Workbook(f'{self.params.NAME}.xlsx')
            sheet_all = workbook.add_worksheet('All')
            sheet_all.autofilter(0,0,len(allItems),len(allItems[0]))
            sheet_all.filter_column('D','x == Sell')
            sheet_all.filter_column('D','x == Donate')
            sheet_all.filter_column('D','x == Garbage')
            sheet_all.filter_column('D','x == Keep')
            cell_orange = workbook.add_format({'font_color':'white','bg_color': 'orange'})
            cell_blue = workbook.add_format({'font_color':'white','bg_color': 'blue'})
            cell_red = workbook.add_format({'font_color':'white','bg_color': 'red'})
            cell_green = workbook.add_format({'font_color':'white','bg_color': 'green'})
            todo_colors = {'Sell':cell_orange,
                           'Donate':cell_blue,
                           'Garbage':cell_red,
                           'Keep':cell_green,
                           }
            todo_sheets = []
            for todo in self.params.TODOS:
                todo_sheets.append((todo[0], workbook.add_worksheet(f'{todo[1]}')))
            for i, item in enumerate(allItems):
                cell_format = todo_colors[item[4]] #todo
                for col in range(len(item)-1):
                    sheet_all.write(i,col,item[col+1], cell_format)
            
            for row in allItems:
                pass
            workbook.close()
            print('Successfully exported!')
        except:
            return
        
    def run(self):
        userInput = None
        #Event Loop
        while self.state != 'EXIT':
            print(f'{self.state}:\n')
            self.displayCommands()
            self.params.TYPES = (self.cursor.execute('SELECT * FROM types').fetchall())
            if self.state == 'ADD':
                self.displayAddFeature(userInput)
            elif self.state == 'TYPE':
                self.displayTypeFeature(userInput)
            elif self.state == 'UPDATE':
                self.displayUpdateFeature(userInput)
            userInput = input('> ')
            clearScreen()
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