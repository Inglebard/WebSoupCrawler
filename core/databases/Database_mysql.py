#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import mysql.connector
from mysql.connector import errorcode

class Database_mysql() :

    def __init__(self,database,database_limit,database_host,database_user,database_password,database_port):

        self.con = None
        self.cur = None

        self.database=database
        self.database_limit=database_limit
        self.database_host=database_host
        self.database_user=database_user;
        self.database_password=database_password
        self.database_port=database_port;

        if(self.database_port == 0) :
            self.database_port=3306

        self.init_database()

    def init_database(self) :
        try:
            self.con = mysql.connector.connect(user=self.database_user, password=self.database_password, host=self.database_host,database=self.database,port=self.database_port)
            self.cur = self.con.cursor()
            self.cur.execute('SELECT version()')
            data = self.cur.fetchone()
            print(data)
            self.cur.execute('''CREATE TABLE IF NOT EXISTS Url(id integer NOT NULL PRIMARY KEY AUTO_INCREMENT, url text, state_analyse TINYINT(2) NOT NULL DEFAULT '0', state_extract TINYINT(2) NOT NULL DEFAULT '0') ENGINE = InnoDB character set utf8mb4 collate utf8mb4_general_ci;''')
            self.cur.execute('''CREATE TABLE IF NOT EXISTS Url_data(id integer NOT NULL PRIMARY KEY AUTO_INCREMENT, url text, data text) character set utf8mb4 collate utf8mb4_general_ci;''')
            self.con.commit()
        except mysql.connector.Error as err:
            if self.con :
                self.con.close()
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)



    def getUrlToAnalyse(self) :
        self.cur.execute('''SELECT * FROM `Url` WHERE `state_analyse`=0 LIMIT %s''',(self.database_limit,))
        return self.cur.fetchall()

    def getUrlToExtract(self) :
        self.cur.execute('''SELECT * FROM `Url` WHERE `state_extract`=0 LIMIT %s''',(self.database_limit,))
        return self.cur.fetchall()

    def updateUrlAnalyzingByIds(self,ids) :
        self.cur.executemany('''UPDATE `Url` SET `state_analyse`=1 WHERE `id`=%s''',ids)
        return self.con.commit()

    def updateUrlExtractingByIds(self,ids) :
        self.cur.executemany('''UPDATE `Url` SET `state_extract`=1 WHERE `id`=%s''',ids)
        return self.con.commit()

    def updateUrlAnalysed(self,id) :
        self.cur.execute('''UPDATE `Url` SET `state_analyse`=3 WHERE `id`=%s''',(id,))
        return self.con.commit()

    def updateUrlExtracted(self,id) :
        self.cur.execute('''UPDATE `Url` SET `state_extract`=3 WHERE `id`=%s''',(id,))
        return self.con.commit()

    def countUrlbyUrl(self,url) :
        self.cur.execute('SELECT count(*) as "nb_url" FROM `Url` WHERE `url`=%s',(url,))
        return self.cur.fetchall()

    def insertUrl(self,url) :
        self.cur.execute('''INSERT INTO `Url`(`url`) VALUES (%s)''',(url,))
        return self.con.commit()

    def countUrl_databyUrlAndData(self,url,data) :
        self.cur.execute('SELECT count(*) as "nb_result" FROM `Url_data` WHERE `url`=%s AND `data`=%s',(url,data))
        return self.cur.fetchall()

    def insertUrl_data(self,url,data) :
        self.cur.execute('''INSERT INTO `Url_data`(`url`, `data`) VALUES (%s,%s)''',(url,data))
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
