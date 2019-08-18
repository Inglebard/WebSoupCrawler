#!/usr/bin/python3
# -*- coding: utf-8 -*-

from core.databases.Database_sqlite import Database_sqlite
from core.databases.Database_mysql import Database_mysql

class Database() :


    DATABASE_TYPE_SQLITE = "sqlite"
    DATABASE_TYPE_MYSQL = "mysql"

    def __init__(self,data_path,database,database_driver,database_limit,database_host,database_user,database_password,database_port):
        self.data_path=data_path
        self.database=database
        self.database_limit=database_limit
        self.database_driver=database_driver;
        self.database_host=database_host
        self.database_user=database_user;
        self.database_password=database_password
        self.database_port=database_port;

    def getDatabase(self) :
        if(self.database_driver == Database.DATABASE_TYPE_SQLITE) :
            return Database_sqlite(self.data_path,self.database,self.database_limit)

        if(self.database_driver == Database.DATABASE_TYPE_MYSQL) :
            return Database_mysql(self.database,self.database_limit,self.database_host,self.database_user,self.database_password,self.database_port)

        return Database_sqlite(self.data_path,self.database,self.database_limit)
