# -*- coding: utf-8 -*-
"""
Attic Sorter

Created on Sat Aug  1 14:02:33 2020

@author: Zane Fadul
"""

import sqlite3
import tabulate

#init Categories
CATEGORIES = ["sell","donate","garbage"]

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
        
#init tables
def create_tables(cursor):
    #init items table
    cursor.execute('''CREATE TABLE items (
                        id INTEGER PRIMARY KEY,
                        type_key INTEGER NOT NULL,
                        FOREIGN KEY (type_key)
                            REFERENCES types (id)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE,
                        desc TEXT NOT NULL,
                        cond TEXT NOT NULL,
                        cat_key INTEGER NOT NULL,
                        FOREIGN KEY (cat_key)
                            REFERENCES categories (id)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE
                        )''')
    
    #init types table
    cursor.execute('''CREATE TABLE types (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL )''')
    
    #init categories table
    cursor.execute('''CREATE TABLE categories (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL )''')
    cursor.execute(f'''INSERT INTO categories (name)
        VALUES {(CATEGORY) for CATEGORY in CATEGORIES};''')
        
if __name__ == '__main__':
    conn, cursor = create_conn('attic.db')
    create_tables(cursor)
    cursor.execute('.tables')
    conn.close()