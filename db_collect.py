import datetime
import time
import sqlite3
from sqlite3 import OperationalError
from sqlite3 import Error
import os
from os import walk
import hashlib
import argparse

class SqliteWorker(object):
    def __init__(self, *args, **kwargs):       
        self.conn = None

    def create_connection(self):
        try:
            self.conn = sqlite3.connect('filedatabase.db')
            print(sqlite3.version)
        except Error as e:
            print(e)
        finally:
            if self.conn:
                cursor = self.conn.cursor()
                return cursor
            else: print('Error. Something wrong with connection.')
    
    def create_table(self, cursor):
        cursor.execute("SELECT name from sqlite_master where type = 'table'")
        result = cursor.fetchall()
        if len(result) == 0:
            
            cursor.execute("""CREATE TABLE filestats
                (file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename text NOT NULL, 
                file_size INTEGER NOT NULL,
                modification_date DATETIME,
                filehash TEXT NOT NULL, 
                record_added DEFAULT CURRENT_TIMESTAMP);""")
            
            print('table created',cursor.fetchall())
        else:
            print('Table found', result)

    
class FileStatsCollector(object):
    def __init__(self):
        # self.dirpath = dir_path
        self.cursor = SW.create_connection()
    def CalcHash(self, file):
        with open(file, 'rb') as f:
            bytes = f.read()
            readable_hash = hashlib.md5(bytes).hexdigest()
            return readable_hash
    
    def ScanFiles(self, dir_path): # insert files information into database 
        sql = '''INSERT INTO filestats(filename, file_size, modification_date, filehash)
              VALUES(?,?,?,?)'''
        
        for path, folder, file in os.walk(dir_path):
            for file_name in file: 
                file_path = os.path.join(path, file_name)
                file_size = os.path.getsize(file_path)
                m_date = os.path.getmtime(file_path)
                readable_date = datetime.datetime.fromtimestamp(m_date).strftime('%Y-%m-%d %H:%M:%S')
                md5_hash = self.CalcHash(file_path)
                
                print(file_path,file_size, '-->',readable_date,'<---', md5_hash)
                self.cursor.execute(sql,(file_path, file_size,readable_date,md5_hash))

        print(self.cursor.lastrowid)
    
    def CheckUpdates(self): # gets through the files on disk and compares them with the database
        print('Check updated files ')
        logs_file = datetime.datetime.now().strftime('%Y-%m-%d-%H_%M') + '.txt'
        f = open(os.path.join("./logs/",logs_file), "a+")
        sql = '''select * from filestats'''
        self.cursor.execute(sql)
        response = self.cursor.fetchall()

        # working through list
        while response:
            file_record = response.pop() # getting a file record from list we get from DB
            file_path = file_record[1]
            current_date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if os.path.exists(file_path):
                print('file exists', current_date_time, file_path)
                
                file_size = os.path.getsize(file_path)
                m_date = os.path.getmtime(file_path)
                readable_date = datetime.datetime.fromtimestamp(m_date).strftime('%Y-%m-%d %H:%M:%S')
                md5_hash = self.CalcHash(file_path)
                current_record = (file_path, file_size, readable_date, md5_hash)
                print(current_record)
                print(response[0][1:-1])
                if current_record == file_record[1:-1]:
                    f.write(current_date_time + ': ' + file_path + ' corresponds to the DB Info.\n')
                    #print(f'File {file_path} is not changed.')
                else:
                    #print(f'File {file_path} is changed.')
                    f.write(current_date_time + ': ' + file_path + ' file has been changed.\n')
            else:
                print('file file_path does not exists')
                f.write(f'{current_date_time}: {file_path} file was not found.\n')
        f.close()

if __name__ == '__main__':
    SW = SqliteWorker()
    cursor = SW.create_connection()
    SW.create_table(cursor)
    FColl = FileStatsCollector()
    # cursor.execute("SELECT name from sqlite_master where type = 'table';")
    # response = cursor.fetchall()
    # cursor.execute("SELECT datetime('now');")
    # print(cursor.fetchall())

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', required=False, help="Put a full path to the directory you want to collect the info.")
    args = parser.parse_args()
# cli parsing code block
    if args.d == None:
        print('Scanning existing records for changes. No parameters has been provided.')
        FColl.CheckUpdates()
    else:
        #checking if it is a valid path

        print(f'Got a directory to add {args.d}')
        print(os.path.isdir(args.d), args.d , ' exists')
        if os.path.isdir(args.d):
            print(f' {args.d} turns to be a valid dir, start to scan')
            dir_path = args.d
            try:
                FColl = FileStatsCollector()
                FColl.ScanFiles(dir_path)
            except OperationalError: print('DB is locked.')
            SW.conn.commit()
            SW.conn.close()

        else:
            print('Not valid dir, terminating...')
# cli parsing code block end