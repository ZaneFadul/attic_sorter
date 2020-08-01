# -*- coding: utf-8 -*-
"""
Attic Sorter

Created on Sat Aug  1 14:02:33 2020

@author: Zane Fadul
"""

import sqlite3
import tkinter as tk

#init Categories
TODOS = [(1,"Sell"), (2,"Donate"), (3,"Garbage"), (4,"Keep")]
CONDITIONS = [(1,"Poor"), (2,"Fair"), (3,"Good"), (4,"Excellent")]

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
def create_tables(conn, cursor):
    #init todos table
    cursor.execute('''CREATE TABLE IF NOT EXISTS todos (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL)''')
    for TODO in TODOS:
        cursor.execute(f'''INSERT INTO todos VALUES ({TODO[0]},"{TODO[1]}")''')
        
    #init types table
    cursor.execute('''CREATE TABLE IF NOT EXISTS types (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL)''')
    
    #init conditions table
    cursor.execute('''CREATE TABLE IF NOT EXISTS conditions (
                        id INTEGER PRIMARY KEY,
                        condition TEXT NOT NULL)''')
    for CONDITION in CONDITIONS:
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


if __name__ == '__main__':
    conn, cursor = create_conn('attic.db')
    window = tk.Tk()
    try:
        if not tables_exist(cursor):
            create_tables(conn, cursor)
        
    except Exception as e:
        print(e)
    finally:
        conn.close()