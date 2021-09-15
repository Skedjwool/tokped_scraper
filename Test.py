import requests
from datetime import datetime 

url = "http://127.0.0.1:5000/"
shopname = input('Enter shop name: ').lower().replace(" ", "")
pagenum = int(input('Enter how many page you want to scrape (Input 0 if you want to scrape all the pages): '))
init_time = datetime.now()
result = requests.post(url + "tokped/" + shopname + '&' + str(pagenum))

try:
    print(result.json())
except:
    print(result)
fin_time = datetime.now()
print("Execution time = ", {fin_time-init_time})