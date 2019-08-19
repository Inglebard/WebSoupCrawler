#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import sqlite3

class Database_sqlite() :

    def __init__(self,data_path,database,database_limit):

        self.con = None
        self.cur = None

        self.data_path=data_path
        self.database=database
        self.database_limit=database_limit

        self.init_database()

    def init_database(self) :
        try:
            print(self.data_path+self.database)
            self.con = sqlite3.connect(self.data_path+self.database)
            self.cur = self.con.cursor()
            self.cur.execute('SELECT SQLITE_VERSION()')
            data = self.cur.fetchone()
            print(data)
            self.cur.execute('''CREATE TABLE IF NOT EXISTS Url(id integer NOT NULL PRIMARY KEY AUTOINCREMENT, url text, state_analyse INTEGER DEFAULT 0, state_extract INTEGER DEFAULT 0)''')
            self.cur.execute('''CREATE TABLE IF NOT EXISTS Url_data(id integer NOT NULL PRIMARY KEY AUTOINCREMENT, url text, data text)''')
            self.con.commit()
        except sqlite3.Error as e :
            print("Error : ", e)
            if self.con :
                self.con.close()
            sys.exit(1)



    def getUrlToAnalyse(self) :
        self.cur.execute('''SELECT * FROM `Url` WHERE `state_analyse`=0 LIMIT ?''',(self.database_limit,))
        return self.cur.fetchall()

    def getUrlToExtract(self) :
        self.cur.execute('''SELECT * FROM `Url` WHERE `state_extract`=0 LIMIT ?''',(self.database_limit,))
        return self.cur.fetchall()

    def updateUrlAnalyzingByIds(self,ids) :
        self.cur.executemany('''UPDATE `Url` SET `state_analyse`=1 WHERE `id`=?''',ids)
        return self.con.commit()

    def updateUrlExtractingByIds(self,ids) :
        self.cur.executemany('''UPDATE `Url` SET `state_extract`=1 WHERE `id`=?''',ids)
        return self.con.commit()

    def updateUrlAnalysed(self,id) :
        self.cur.execute('''UPDATE `Url` SET `state_analyse`=3 WHERE `id`=?''',(id,))
        return self.con.commit()

    def updateUrlExtracted(self,id) :
        self.cur.execute('''UPDATE `Url` SET `state_extract`=3 WHERE `id`=?''',(id,))
        return self.con.commit()

    def countUrlbyUrl(self,url) :
        self.cur.execute('SELECT count(*) as "nb_url" FROM `Url` WHERE `url`=?',(url,))
        return self.cur.fetchall()

    def insertUrl(self,url) :
        self.cur.execute('''INSERT INTO `Url`(`url`) VALUES (?)''',(url,))
        return self.con.commit()

    def countUrl_databyUrlAndData(self,url,data) :
        self.cur.execute('SELECT count(*) as "nb_result" FROM `Url_data` WHERE `url`=? AND `data`=?',(url,data))
        return self.cur.fetchall()

    def insertUrl_data(self,url,data) :
        self.cur.execute('''INSERT INTO `Url_data`(`url`, `data`) VALUES (?,?)''',(url,data))
        return self.con.commit()

    def resetAnalysing(self) :
        self.cur.execute('''UPDATE `Url` SET `state_analyse`=0 WHERE `state_analyse`=1''')
        return self.con.commit()

    def resetExtracting(self) :
        self.cur.execute('''UPDATE `Url` SET `state_extract`=0 WHERE `state_extract`=1''')
        return self.con.commit()

    def close(self) :
        if self.con :
            self.con.close()
