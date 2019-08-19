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
            self.cur.execute('''CREATE TABLE IF NOT EXISTS Url(id integer NOT NULL PRIMARY KEY AUTO_INCREMENT, url text, state integer, process integer) character set utf8 collate utf8mb4_general_ci;''')
            self.cur.execute('''CREATE TABLE IF NOT EXISTS Url_data(id integer NOT NULL PRIMARY KEY AUTO_INCREMENT, url text, data text) character set utf8 collate utf8mb4_general_ci 	;''')
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



    def getUrlbyState(self,state) :
        self.cur.execute('''SELECT * FROM `Url` WHERE state=%s LIMIT %s''',(state,self.database_limit))
        return self.cur.fetchall()

    def getUrlbyStateAndId(self,state,id) :
        self.cur.execute('''SELECT * FROM `Url` WHERE state=%s and id=%s''',(state,id))
        return self.cur.fetchone()

    def updateUrlbyStateAndId(self,state,id) :
        self.cur.execute('''UPDATE `Url` SET `state`=%s WHERE id=%s''',(state,id))
        return self.con.commit()

    def countUrlbyUrl(self,url) :
        self.cur.execute('SELECT count(*) as "nb_url" FROM `Url` WHERE url=%s',(url,))
        return self.cur.fetchall()

    def insertUrl(self,url,state) :
        self.cur.execute('''INSERT INTO `Url`(`url`, `state`) VALUES (%s,%s)''',(url,state))
        return self.con.commit()

    def countUrl_databyUrlAndData(self,url,data) :
        self.cur.execute('SELECT count(*) as "nb_result" FROM `Url_data` WHERE url=%s AND data=%s',(url,data))
        return self.cur.fetchall()

    def insertUrl_data(self,url,data) :
        self.cur.execute('''INSERT INTO `Url_data`(`url`, `data`) VALUES (%s,%s)''',(url,data))
        return self.con.commit()

    def close(self) :
        if self.con :
            self.con.close()
