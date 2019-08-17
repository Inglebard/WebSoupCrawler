class logger:
    def __init__(self):
        print("Logger init")

    def analysed(self, url, html_data, parent_url):
        print("Analysed : "+parent_url.geturl()+", discovered : "+url)

    def extracted(self, data, html_data, parent_url):
        print("Extraced from " + parent_url + " : "+str(data))
