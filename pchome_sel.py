import requests
import re
import pprint
import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time


# connect to MySQL
DB_NAME = 'PC_home_sel'
try:
  cnx = mysql.connector.connect(user='#######', password='#######', 
                                host='#######', database='#######')
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
  print('succeessfully connected to MySQL swver.')


cursor = cnx.cursor()


# creat database
def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


try:
    cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("Database {} does not exists.".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print("Database {} created successfully.".format(DB_NAME))
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)

# creat table
TABLES = {}
TABLES['products'] = (
    "CREATE TABLE `products` ("
    "  `id` int NOT NULL AUTO_INCREMENT,"
    "  `name` varchar(50) NOT NULL,"
    "  `price` int NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")


for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")


# insert data
# 單純只是路徑(也可使用絕對路徑)
chromedriver = 'chromedriver.exe'
driver = webdriver.Chrome(chromedriver)
driver.get('https://shopping.pchome.com.tw/')

search = driver.find_element(By.XPATH, '//*[@id="root"]/div/header/div[2]/div[1]/div/div/div/div/div[3]/input')
search.send_keys('曲面螢幕')
search.send_keys(Keys.RETURN)

time.sleep(3)

names = driver.find_elements(By.CLASS_NAME, 'prod_name')
prices = driver.find_elements(By.CLASS_NAME, 'price')[:-1:]

names_texts = []
for name in names:
    if len(name.text) >= 50:
        name_text = str(name.text)[:50]
    names_texts.append(name_text)

prices_ints = []
for price in prices:
    price_int = int(price.text[1:])
    prices_ints.append(price_int)



product_tulpes = list(zip(names_texts, prices_ints))
for product_tulpe in product_tulpes:
    print(product_tulpe)

add_product = ("INSERT INTO products "
               "(name, price) "
               "VALUES (%s, %s)")


for product_tulpe in  product_tulpes:
        cursor.execute(add_product, product_tulpe)



# r = requests.get('https://ecshweb.pchome.com.tw/search/v3.3/all/results?q=%E6%9B%B2%E9%9D%A2%E8%9E%A2%E5%B9%95&page=1&sort=sale/dc')
# print(r)
# if r.status_code == requests.codes.ok:
#     data = r.json()
    
#     add_product = ("INSERT INTO products "
#                "(name, price) "
#                "VALUES (%s, %s)")

#     for product in data['prods']:
#         name = product['name']
#         if len(name) >= 50:
#             name = name[:50]
#         price = product['price']
#         print(name)
#         print(price)
#         data_product = (name, price)
#         cursor.execute(add_product, data_product)

cnx.commit()
print('close')

driver.close()
cursor.close()
cnx.close()




