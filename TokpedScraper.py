from flask import Flask
from flask_restful import Api, Resource, reqparse
import requests
from bs4 import BeautifulSoup
import json

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

def write_content(itemname, itempic, itemprice, itemdesc):
    content = {
        "name":itemname,
        "images":itempic,
        "price":itemprice,
        "description":itemdesc
    }
    return content

def write_content_ext(itemname, itempic, itemprice, itemdesc, itemtags, itemstock):
    content = {
        "name":itemname,
        "images":itempic,
        "price":itemprice,
        "description":itemdesc,
        "tags":itemtags,
        "stock":itemstock
    }
    return content

def write_json(data):
    if len(data) > 0:
        result = {
            "message":"Success",
            "data":{
                "posts":data
            }
        }
    else:
        result = {
            "message":"Failed",
            "data":{
                "posts":"Invalid shop name"
            }
        }
    return result

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
        itemtags = []
        itemstock = 0
        itemlink = container.a
        itempage = get_page(itemlink.get('href'))
        itemname = itempage.find('div', class_='css-jmbq56').h1.text
        itempic = itempage.find('div', class_='css-1q3zvcj').img.get('src')
        # temp2 = itempage.find_all('div', class_='css-1aplawl') #attemp to add preview link (suspended)
        # print(temp2)
        # for link in temp2:
        #     link.replace('200-square', '500-square').replace('.webp?ect=4g', '')
        #     print('test2: ' + link)
        #     temp.append(temp2)
        try:
            temp = itempage.find('div', class_='css-70qvj9').text
            itemprice['before-discount'] = int(temp[temp.index('Rp'):].replace('Rp', '').replace('.', ''))
            itemprice['after-discount'] = int(itempage.find('div', class_='css-aqsd8m').div.text)
        except:
             itemprice['after-discount'] = int(itempage.find('div', class_='css-aqsd8m').div.text.replace('Rp', '').replace('.', ''))
        try:
            itemdesc = str(itempage.find(attrs={'data-testid':'lblPDPDescriptionProduk'})).replace('<div data-testid="lblPDPDescriptionProduk">', '').replace('</div>', '').replace('<br/>','\n')
        except:
            itemdesc = 'No Description Available'
        # temp = itempage.find('div', class_='css-17o7uaz') #Grab item tags here (failed)
        # print(temp)
        # for list in temp.find_all('li', class_='css-1xfnjem'):
        #     itemtags.append(list.a.text)
        # print(itemtags)
        # itemstock = itempage.find('div', class_='css-1a2eh9p').b.text #grab item stock
        data.append(write_content(itemname, itempic, itemprice, itemdesc))
    return data

def scrape(shopname):
    currpage = 0
    page = []
    page_div = []
    data = []
    while True:
        itemlink = ""
        currpage+=1
        page_div = get_page_spec(generate_link(shopname, currpage), 'div', 'css-1sn1xa2')
        if len(page_div)>0:
            data.append(scrape_info(page_div))
            print('Fetched ' + str(len(page_div)) +' from page: ' + str(currpage))
        else:
            break
    return write_json(data)

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
            print('Fetching ' + str(len(page_div)) +' from page: ' + str(currpage))
        else:
            break
    return write_json(data)

if __name__ == "__main__":
    app.run(debug=True)

