#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sqlite3
import sys
import argparse
import urllib.request
import re
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup



class WebSoupCrawler() :

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

        self.root_url_parsed="";
        self.con = None
        self.cur = None


        self.parse_args()
        self.init_process()

    def parse_args(self):

        parser = argparse.ArgumentParser(description="Simple web crawler.")
        parser.add_argument('-u', '--url', metavar='url', default="", type=str, help="Root url to parse.")
        parser.add_argument('-d', '--delay', metavar='request_delay', default=1, type=float, help="Delay between two requests.")
        parser.add_argument('-db', '--database', metavar='database', type=str, help="Sqlite database to store result", required=True)
        parser.add_argument('-p', '--process', metavar='process', default="analyse", choices=['analyse', 'extract'], help="analyse : To parse url in web pages \n extract : to retrieve data")
        parser.add_argument('-s', '--selector', metavar='selector', default="", type=str, help="Css selector to extract data. Ignore if -p analyse used.")
        parser.add_argument('-f', '--follow_url', metavar='follow_url', default="", type=str, help="Add url (regex) to follow. Default : Current domain only")
        parser.add_argument('-e', '--exclude_url', metavar='exclude_url', default="", type=str, help="Exclude url (regex) to follow. Default : Current domain only")

        args = parser.parse_args()


        self.url=args.url.strip();
        self.delay=args.delay;
        self.database=args.database;
        self.process=args.process;
        self.selector=args.selector;
        self.follow_url=args.follow_url;
        self.exclude_url=args.exclude_url

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

        try:
            self.con = sqlite3.connect(self.database)
            self.cur = self.con.cursor()
            self.cur.execute('SELECT SQLITE_VERSION()')
            data = self.cur.fetchone()
            self.cur.execute('''CREATE TABLE IF NOT EXISTS Url(id integer NOT NULL PRIMARY KEY AUTOINCREMENT, url text, state integer, process integer)''')
            self.cur.execute('''CREATE TABLE IF NOT EXISTS Url_data(id integer NOT NULL PRIMARY KEY AUTOINCREMENT, url text, data text)''')
            self.con.commit()

            if self.process == WebSoupCrawler.PROCESS_ANALYSE :
                try :
                    html = urllib.request.urlopen(self.url).read()
                except urllib.error.URLError as e :
                    print(e.reason)
                    sys.exit(1)
                except urllib.error.HTTPError as e1 :
                    print(e1.reason)
                    sys.exit(1)

                try :
                    self.store_url(html,self.root_url_parsed)
                    self.mainloop()
                except sqlite3.Error as e :
                    print("Error : ", e)
                    sys.exit(1)
                finally :
                    if self.con :
                        self.con.close()

            elif self.process == WebSoupCrawler.PROCESS_EXTRACT :
                try :
                    self.mainloop()
                except sqlite3.Error as e :
                    print("Error : ", e)
                    sys.exit(1)
                finally :
                    if self.con :
                        self.con.close()
        except sqlite3.Error as e :
            print("Error : ", e)
            sys.exit(1)
        finally :
            if self.con :
                self.con.close()



    def mainloop(self) :
        continue_loop=True
        while continue_loop :
            result = ()
            if self.process == WebSoupCrawler.PROCESS_ANALYSE :
                result=self.cur.execute('''SELECT * FROM `Url` WHERE state=?''',(WebSoupCrawler.STATE_DISCOVERED,))
            elif self.process == WebSoupCrawler.PROCESS_EXTRACT :
                result=self.cur.execute('''SELECT * FROM `Url` WHERE state=?''',(WebSoupCrawler.STATE_ANALYSED,))

            rows = self.cur.fetchall()
            print(len(rows))
            if len(rows) <= 0 :
                continue_loop = False
            else :
                continue_loop = True
                for row in rows :
                    datarow=()
                    result2=()

                    if self.process == WebSoupCrawler.PROCESS_ANALYSE :
                        result2=self.cur.execute('''SELECT * FROM `Url` WHERE state=? and id=?''',(WebSoupCrawler.STATE_DISCOVERED,row[0]))
                    elif self.process == WebSoupCrawler.PROCESS_EXTRACT :
                        result2=self.cur.execute('''SELECT * FROM `Url` WHERE state=? and id=?''',(WebSoupCrawler.STATE_ANALYSED,row[0]))

                    datarow=self.cur.fetchone()
                    if datarow:
                        if self.process == WebSoupCrawler.PROCESS_ANALYSE and datarow[2] == WebSoupCrawler.STATE_DISCOVERED:
                            try :
                                htmlresult = urllib.request.urlopen(datarow[1]).read()
                                self.store_url(htmlresult,urlparse(datarow[1]))
                            except urllib.error.URLError as e :
                                print(e.reason)
                            except urllib.error.HTTPError as e1 :
                                print(e1.reason)
                            self.cur.execute('''UPDATE `Url` SET `state`=? WHERE id=?''',(WebSoupCrawler.STATE_ANALYSED,datarow[0]))
                            self.con.commit()

                        if self.process == WebSoupCrawler.PROCESS_EXTRACT and datarow[2] == WebSoupCrawler.STATE_ANALYSED:
                            try :
                                htmlresult = urllib.request.urlopen(datarow[1]).read()
                                self.extract_data(htmlresult,datarow[1])
                            except urllib.error.URLError as e :
                                print(e.reason)
                            except urllib.error.HTTPError as e1 :
                                print(e1.reason)
                            self.cur.execute('''UPDATE `Url` SET `state`=? WHERE id=?''',(WebSoupCrawler.STATE_EXTRACTED,datarow[0]))
                            self.con.commit()
                        time.sleep(self.delay)

    def store_url(self,html_data,parent_url) :
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
                result=self.cur.execute('SELECT count(*) as "nb_url" FROM `Url` WHERE url=?',(url_str,))
                rows=self.cur.fetchall()
                for row in rows :
                    if row[0] == 0 :
                        try :
                            self.cur.execute('''INSERT INTO `Url`(`url`, `state`) VALUES (?,?)''',(url_str,WebSoupCrawler.STATE_DISCOVERED))
                            self.con.commit()
                        except e:
                            print('Error : ', e.reason)

    def extract_data (self,html_data,parent_url) :
        htmlparse = BeautifulSoup(html_data,'html.parser')
        data=[]
        for selector in self.selector.split(",") :
            data+=htmlparse.select(selector)
        if(data) :
            result=self.cur.execute('SELECT count(*) as "nb_result" FROM `Url_data` WHERE url=? AND data=?',(parent_url,str(data)))
            rows=self.cur.fetchall()
            for row in rows :
                if row[0] == 0 :
                    try :
                        self.cur.execute('''INSERT INTO `Url_data`(`url`, `data`) VALUES (?,?)''',(parent_url,str(data)))
                        self.con.commit()
                    except e:
                        print('Error : ', e.reason)

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

if __name__ == "__main__":
    WebSoupCrawler()
