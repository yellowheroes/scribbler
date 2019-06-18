'''
Created on 28 May 2019

@author: Robert
'''
import sqlite3
from sqlite3 import Error
#from adodbapi.test.adodbapitestconfig import mdb_name
#from adodbapi.examples.xls_read import conn
#from pandas.io import sql

class DbLite:
    '''
    connect to a database
    if db_name does not exist, it will be created
    '''
    def connect(self, db_name = None):
        """ create a SQLite database connection - if db_name does not exist, it will be created """
        try:
            conn = sqlite3.connect(db_name)
            return conn
        except Error as e:
            print('error connecting to database:', e)
            return False
    
    def open(self, db_name):
        try:
            print('now in DbLite()::open()')
            conn = sqlite3.open(db_name)
            return conn
        except:
            print('error: could not OPEN db_name')
            return 1
            
    '''
    create a table
    '''      
    def create_tbl(self, conn = None, sql = None):
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            return True
        except Error as e:
            print(e)
    
    '''
    create a new row
    '''
    def create(self, conn = None, sql = None, data = None):
        try:
            cursor = conn.cursor()
            cursor.execute(sql, data)
            id = cursor.lastrowid
            conn.commit() # commit changes
            return id
        except Error as e:
            print(e)
    
    '''
    read a row
    '''
    def read(self, conn = None, sql = None, id = None):
        try:
            cursor = conn.cursor()
            if id != None:
                cursor.execute(sql, (id,)) # prepared statement
            else:
                cursor.execute(sql) # no prepared statement, we read all rows from table
            
            rows = cursor.fetchall() # get all matches
            #conn.commit() # commit changes
            return rows # return all matches
        except Error as e:
            print(e)
    
    '''
    update a row
    '''
    def update(self, conn = None, sql = None, data = None):
        try:
            cursor = conn.cursor()
            cursor.execute(sql, data)
            id = cursor.lastrowid
            conn.commit() # commit changes
            return id
        except Error as e:
            print(e)
    
    '''
    delete a row
    '''
    def delete(self, conn = None, sql = None, id = None):
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (id,))
            id = cursor.lastrowid
            conn.commit() # commit changes
            return id
        except Error as e:
            print(e)
    
    '''
    drop table
    '''
    def drop(self, conn = None):
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            #id = cursor.lastrowid
            conn.commit() # commit changes
            return 'Status: table dropped'
        except Error as e:
            print(e)