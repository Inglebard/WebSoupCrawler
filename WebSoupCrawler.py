#!/usr/bin/python3
# -*- coding: utf-8 -*-

import hashlib
import urllib
import sys
import argparse
import requests
import re
import os
import time
import importlib
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from core.Database import Database
import glob

class WebSoupCrawler() :

    DATA_PATH = "data/"
    CACHE_PATH = "cache/"
    MODULES_PATH = "modules/"

    MODULES_DIR = "modules"

    PROCESS_ANALYSE = "analyse"
    PROCESS_EXTRACT = "extract"

    STATE_DISCOVERED = 0
    STATE_ANALYSED = 1
    STATE_EXTRACTED = 2

    def __init__(self):


        self.url="";
        self.delay="";
        self.database="";
        self.process="";
        self.selector="";
        self.follow_url="";
        self.exclude_url="";

        self.cache=False;
        self.database_limit="";
        self.database_driver="";
        self.database_host="";
        self.database_user="";
        self.database_password="";
        self.database_port="";

        self.root_url_parsed="";
        self.db = None
        self.dynamic_modules = []



        dynamic_modules_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),WebSoupCrawler.MODULES_PATH)
        dynamic_modules_path=os.path.join(dynamic_modules_dir,"*.py")
        modules_files = glob.glob(dynamic_modules_path)

        for module_path in modules_files:
            basename_module=os.path.basename(module_path)[:-3]
            module=importlib.import_module(WebSoupCrawler.MODULES_DIR+'.'+basename_module)
            module_class = getattr(module, basename_module)
            self.dynamic_modules.append(module_class())

        self.parse_args()
        self.init_process()

    def parse_args(self):

        parser = argparse.ArgumentParser(description="Simple web crawler.")
        parser.add_argument('-u', '--url', metavar='url', default="", type=str, help="Root url to parse.")
        parser.add_argument('-d', '--delay', metavar='request_delay', default=1, type=float, help="Delay between two requests.")
        parser.add_argument('-p', '--process', metavar='process', default="analyse", choices=['analyse', 'extract'], help="analyse : To parse url in web pages \n extract : to retrieve data")
        parser.add_argument('-s', '--selector', metavar='selector', default="", type=str, help="Css selector to extract data. Ignore if -p analyse used.")
        parser.add_argument('-f', '--follow_url', metavar='follow_url', default="", type=str, help="Add url (regex) to follow. Default : Current domain only")
        parser.add_argument('-e', '--exclude_url', metavar='exclude_url', default="", type=str, help="Exclude url (regex) to follow. Default : Current domain only")

        parser.add_argument('-c', '--cache', action='store_true', required=False,  help="Cache html result when requested.Can improve performance but will use disk space. Default : False")
        parser.add_argument('-ct', '--cache_timeout', metavar='cache_timeout', default=0, type=int, help="Cache timeout in seconds. Default : 0 (no timeout)")

        parser.add_argument('-db', '--database', metavar='database', type=str, help="Sqlite database to store result", required=True)
        parser.add_argument('-db_l', '--database_limit', metavar='limit', default=100, type=int, help="Limit request to database. Allow multiple instance Default: 100")
        parser.add_argument('-db_d', '--database_driver', metavar='database_driver', default="sqlite", choices=['sqlite', 'mysql', 'mongodb'], help="Select database type ('sqlite', 'mysql', 'mongodb)")
        parser.add_argument('-db_h', '--database_host', metavar='database_host', default="localhost", type=str, help="Database host. Default: localhost")
        parser.add_argument('-db_u', '--database_user', metavar='database_user', default="", type=str, help="Database user")
        parser.add_argument('-db_pwd', '--database_password', metavar='database_password', default="", type=str, help="Database password")
        parser.add_argument('-db_p', '--database_port', metavar='database_port', default=0, type=int, help="Database port. Default : Will use default port (Depend of database type)")

        args = parser.parse_args()

        self.url=args.url.strip();
        self.delay=args.delay;
        self.database=args.database;
        self.process=args.process;
        self.selector=args.selector;
        self.follow_url=args.follow_url;
        self.exclude_url=args.exclude_url

        self.cache=args.cache;
        self.cache_timeout=args.cache_timeout;

        self.database_limit=args.database_limit
        self.database_driver=args.database_driver;
        self.database_host=args.database_host
        self.database_user=args.database_user;
        self.database_password=args.database_password
        self.database_port=args.database_port;

        if self.process == WebSoupCrawler.PROCESS_ANALYSE and not self.url :
            sys.stderr.write('Error: %s\n' % "url parameter is required to analyse webpage")
            parser.print_help()
            sys.exit(2)

        if self.process == WebSoupCrawler.PROCESS_EXTRACT and not self.selector :
            sys.stderr.write('Error: %s\n' % "selector parameter is required to analyse webpage")
            parser.print_help()
            sys.exit(2)

    def init_process(self) :

        self.root_url_parsed=urlparse(self.url)

        self.db=Database(os.path.join(os.path.dirname(os.path.abspath(__file__)),WebSoupCrawler.DATA_PATH),self.database,self.database_driver,self.database_limit,self.database_host,self.database_user,self.database_password,self.database_port).getDatabase()


        if self.process == WebSoupCrawler.PROCESS_ANALYSE :
            html,cached =  self.fetch_data(self.url)
            self.store_url(html,self.root_url_parsed)
            self.mainloop()

        elif self.process == WebSoupCrawler.PROCESS_EXTRACT :
            self.mainloop()



    def mainloop(self) :
        continue_loop=True
        while continue_loop :
            result = ()
            rows=''
            if self.process == WebSoupCrawler.PROCESS_ANALYSE :
                rows=self.db.getUrlbyState(WebSoupCrawler.STATE_DISCOVERED)
            elif self.process == WebSoupCrawler.PROCESS_EXTRACT :
                rows=self.db.getUrlbyState(WebSoupCrawler.STATE_ANALYSED)

            print(len(rows))
            if len(rows) <= 0 :
                continue_loop = False
            else :
                continue_loop = True
                for row in rows :
                    datarow=()
                    result2=()

                    if self.process == WebSoupCrawler.PROCESS_ANALYSE :
                        datarow=self.db.getUrlbyStateAndId(WebSoupCrawler.STATE_DISCOVERED,row[0])
                    elif self.process == WebSoupCrawler.PROCESS_EXTRACT :
                        datarow=self.db.getUrlbyStateAndId(WebSoupCrawler.STATE_ANALYSED,row[0])

                    if datarow:
                        cached=False
                        if self.process == WebSoupCrawler.PROCESS_ANALYSE and datarow[2] == WebSoupCrawler.STATE_DISCOVERED:
                            htmlresult, cached =  self.fetch_data(datarow[1])
                            self.store_url(htmlresult,urlparse(datarow[1]))
                            self.db.updateUrlbyStateAndId(WebSoupCrawler.STATE_ANALYSED,datarow[0])

                        if self.process == WebSoupCrawler.PROCESS_EXTRACT and datarow[2] == WebSoupCrawler.STATE_ANALYSED:
                            htmlresult, cached = self.fetch_data(datarow[1])
                            self.extract_data(htmlresult,datarow[1])
                            self.db.updateUrlbyStateAndId(WebSoupCrawler.STATE_EXTRACTED,datarow[0])
                        if not cached :
                            time.sleep(self.delay)

    def store_url(self,html_data,parent_url) :
        print(parent_url)
        htmlparse = BeautifulSoup(html_data,'html.parser')
        for link in htmlparse.find_all('a') :
            url_str=link.get('href')
            currenturl=urlparse(url_str)

            if str(url_str).startswith('..') :
                split_current_url=self.root_url_parsed.geturl().rsplit('/', 1)
                base_url=split_current_url[0]
                end_url="/"+url_str.replace("../","")
                new_url=base_url+end_url
                currenturl=urlparse(new_url)

            if currenturl.netloc=='' and currenturl.scheme=='' :
                url_str=self.root_url_parsed.scheme+'://'+self.root_url_parsed.netloc+url_str
            elif currenturl.netloc=='' :
                url_str=self.root_url_parsed.netloc+url_str
            elif currenturl.scheme=='' :
                url_str=self.root_url_parsed.netloc+url_str
            currenturl=urlparse(url_str)

            if self.to_follow_url(currenturl) :
                rows=self.db.countUrlbyUrl(url_str)
                for row in rows :
                    if row[0] == 0 :
                        for module in self.dynamic_modules :
                            module.analysed(url_str,html_data,parent_url)
                        self.db.insertUrl(url_str,WebSoupCrawler.STATE_DISCOVERED)

    def extract_data (self,html_data,parent_url) :
        htmlparse = BeautifulSoup(html_data,'html.parser')
        data=[]
        for selector in self.selector.split(",") :
            data+=htmlparse.select(selector)
        if(data) :
            rows=self.db.countUrl_databyUrlAndData(parent_url,str(data))
            for row in rows :
                if row[0] == 0 :
                    for module in self.dynamic_modules :
                        module.extracted(data,html_data,parent_url)
                    self.db.insertUrl_data(parent_url,str(data))

    def to_follow_url(self,currenturl) :
        if self.follow_url :
            regexfollow = re.compile(self.follow_url)
            if currenturl.netloc == self.root_url_parsed.netloc or regexfollow.match(currenturl.geturl()):
                return True
            else :
                return False

        if self.exclude_url :
            regexexclude = re.compile(self.exclude_url)
            if currenturl.netloc != self.root_url_parsed.netloc or regexexclude.match(currenturl.geturl()):
                return False
            else :
                return True

        if not self.exclude_url and not self.follow_url :
            if currenturl.netloc == self.root_url_parsed.netloc :
                return True
            else :
                return False

    def request_data(self,url) :
        html=""
        try :
            html =  requests.get(url).text
        except :
            print('Error : ', sys.exc_info()[0])
        return html

    def fetch_data(self,url) :

        html=""
        cached=False;
        if self.cache == True :
            #cachefilename=urllib.parse.quote_plus(url)+".html"

            url_parsed=urlparse(url)
            cachefilename=urllib.parse.quote_plus(url_parsed.netloc)+"_"+hashlib.sha512(url.encode()).hexdigest()+".html"

            cache_file_path=WebSoupCrawler.CACHE_PATH+cachefilename
            if os.path.isfile(cache_file_path) == True and (self.cache_timeout == 0 or (time.time() - os.path.getmtime(cache_file_path)) < self.cache_timeout) :
                with open(cache_file_path, 'r') as cache_file:
                    html = cache_file.read()
                    cached=True
            else :
                html=self.request_data(url)
                with open(cache_file_path, 'w') as cache_file:
                    cache_file.write(html)
        else :
            html=self.request_data(url)

        return html,cached

if __name__ == "__main__":
    WebSoupCrawler()
