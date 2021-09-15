from flask import Flask
from flask_restful import Api, Resource, reqparse
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

app = Flask(__name__)
api = Api(app)

# scraper_args = reqparse.RequestParser()
# scraper_args.add_argument("shopname", type=str, help="")
# scraper_args.add_argument("pagenum", type=int, help="")

class Scraper(Resource):
    def post(self, shopname, pagenum):
        if pagenum == 0:
            return scrape(shopname)
        elif pagenum > 0:
            return scrape_some(shopname, pagenum)
    
    # def put(self, user_query):
    #     #dosmt
    #     return 

api.add_resource(Scraper, "/tokped/<string:shopname>&<int:pagenum>")

def testing_req(user_query):
    if "shopname" in user_query and "pagenum" in user_query:
        shopname =  user_query[user_query.index('shopname='):user_query.index('&')].replace('shopname=', '')
        print(shopname)
        pagenum = int(user_query[len(user_query)-1])
        print(pagenum)
        if pagenum == 0:
            data = {
                "message":"Success",
                "data":scrape(shopname)
                }
            return json.dumps(data)
        elif pagenum > 0:
            data = {
                "message":"Success",
                "data":scrape_some(shopname, pagenum)
            }
            return json.dumps(data)
    data = {
        "message":"Failed",
        "data":"What are you doing here, man?"
    }
    return json.dumps(data)

def generate_link(shopname, currpage):
    fullurl = 'https://www.tokopedia.com/' + shopname + '/product/page/' + str(currpage)
    return fullurl

def get_page(fullurl):
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"
    }
    r = requests.get(fullurl, headers=headers, timeout=10)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup

def get_page_spec(fullurl, tag, tagclass):
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"
    }
    r = requests.get(fullurl, headers=headers, timeout=10)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup.find_all(tag, class_= tagclass)

def write_json(itemname, itempic, itemprice, itemdesc):
    jsoncontent = {
        "name":itemname,
        "images":itempic,
        "price":itemprice,
        "description":itemdesc
    }
    return jsoncontent

def scrape_info(page_div):
    data = []
    for container in page_div:
        itemname = ""
        itempic = []
        itemprice = {
            "before-discount":0,
            "after-discount":0
        }
        itemdesc = ""
        itemtag = []
        itemlink = container.a
        itempage = get_page(itemlink.get('href'))
        itemname = itempage.find('div', class_='css-jmbq56').h1.text
        itempic = itempage.find('div', class_='css-1q3zvcj').img.get('src')
        # temp2 = itempage.find_all('div', class_='css-1aplawl')
        # print(temp2)
        # for link in temp2:
        #     link.replace('200-square', '500-square').replace('.webp?ect=4g', '')
        #     print('test2: ' + link)
        #     break
        # temp.append(temp2)
        try:
            itemprice['before-discount'] = int(itempage.find('p', class_='css-18rr7u8').text.replace('Rp', '').replace('.', ''))
            itemprice['after-discount'] = int(itempage.find('div', class_='css-aqsd8m').div.text.replace('Rp', '').replace('.', ''))
        except:
             itemprice['after-discount'] = int(itempage.find('div', class_='css-aqsd8m').div.text.replace('Rp', '').replace('.', ''))
        try:
            itemdesc = itempage.find('div', class_='css-1k1relq').div.text
        except:
            itemdesc = 'No Description Available'
        count = 0
        itemtag.append(itempage.find('li', class_='css-1xfnjem').a.text)
        data.append(write_json(itemname, itempic, itemprice, itemdesc))
    return data

def scrape(shopname):
    currpage = 0
    page = []
    page_div = []
    data = []
    while True:
        itemlink = ""
        currpage+=1
        try:
            page_div = get_page_spec(generate_link(shopname, currpage), 'div', 'css-1sn1xa2')
            if len(page_div)>0:
                print('Current Page: ' + str(currpage))
                data.append(scrape_info(page_div))
            else:
                break
        except:
            data = {
                "message":"Failed",
                "data":"Invalid shop name"
            }
            break
    return data

def scrape_some(shopname, pagenum):
    itemlink = ""
    page = []
    page_div = []
    data = []
    currpage = 0
    while currpage < pagenum:
        itemlink = ""
        currpage+=1
        page_div = get_page_spec(generate_link(shopname, currpage), 'div', 'css-1sn1xa2')
        if len(page_div)>0:
            data.append(scrape_info(page_div))
        else:
            break
    return data

if __name__ == "__main__":
    app.run(debug=True)

