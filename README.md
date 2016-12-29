# WebSoupCrawler

```
usage: WebSoupCrawler.py [-h] [-u url] [-d request_delay] -db database
                         [-p process] [-s selector] [-f follow_url]
                         [-e exclude_url]
```


## First of all

WebSoupCrawler require BeautifulSoup to works properly.

WebSoupCrawler is a really simple web crawler. It may contains bug and is not perfect. I'm pretty sure than other web crawlers are better. I do not recommend to use WebSoupCrawler in production environnment.

## Why ?

Because a lot of website use templating system, it's easy to retrieve some data. For example, a price on a e-commerce website is always at the same place.


## How it works

WebSoupCrawler works in two steps.

##### Analyze
First, you need to analyze the content :

` ./WebSoupCrawler.py -u "https://play.google.com/" -db googleplay.sqlite3 -p analyse `

This command will save all links in sqlite table :
```
Table : Url
id|url|state(0=discovered,1=Analysed,2=Extracted)|
1|https://play.google.com/store/apps|2|
2|https://play.google.com/apps|2|
3|https://play.google.com/store/apps/category/GAME|2|
4|https://play.google.com/store/apps/category/FAMILY|2|
5|https://play.google.com/store/apps/collection/editors_choice|2|

```


##### Extract

` ./WebSoupCrawler.py -s "title" -db googleplay.sqlite3 -p extract `

This command extract the title on all the page and save in on another table of the database :

```
Table : Url_data
id|url|data|
1|https://play.google.com/store/apps|[<title id="main-title">Applications Android sur Google Play</title>]
2|https://play.google.com/apps|[<title>Google Play</title>]
3|https://play.google.com/store/apps/category/GAME|[<title id="main-title">Jeux – Applications Android sur Google Play</title>]
4|https://play.google.com/store/apps/category/FAMILY|[<title id="main-title">Famille – Applications Android sur Google Play</title>]
5|https://play.google.com/store/apps/collection/editors_choice|[<title id="main-title">Choix de l'ĂŠquipe â Applications Android sur GoogleÂ Play</title>]
```

You can also add mutiple selector to extract data :

` ./WebSoupCrawler.py -s "title,div.something,#footer" -db googleplay.sqlite3 -p extract `


When all the data are extracted, you can explorer them whit a sqlite browser like : [sqlitebrowser](http://sqlitebrowser.org/)
