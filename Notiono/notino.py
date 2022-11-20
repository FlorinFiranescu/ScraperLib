import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
import os
import random
import pandas as pd

#import the productDatabase lib

from productDatabase.MySqlProductDatabase import *
from productDatabase.ProductTable import *
from productDatabase.Product import *

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# page specific
productContainer_divClass = "sc-bcXHqe sc-kImNAt".split(' ')
productsContainer_divClass = "lmHOFQ"
nextPage_xPath='//*[@id="productListWrapper"]/div[3]/div/div[2]'
# product specific
productBrand_h2Class = "sc-cCjUiG sc-dwnOUR grMBfg jIQpuX".split(' ')
productTitle_h3Class = "sc-cjibBx sc-UpCWa gmnpuZ isHfcC".split(' ')
productDescription_pClass = "sc-ZqFbI dacIKO".split(' ')
productPrice_spanClass = "fAAkfx".split(' ')
productLink_hrefClass = "sc-ehvNnt cNFvcb".split(' ')
# container class
class product:
    def __init__(self):
        self.brand = ""
        self.title = ""
        self.description = ""
        self.base_price = 0.0
        self.reduced_price = 0.0
        self.link = ""

    def obj2list(self):
        return [self.title, self.description, self.base_price, self.reduced_price, self.link]

    def __str__(self):
        return f"Title : {self.title}\nBrand: {self.brand}\nDescription : {self.description}\nBase price : {self.base_price}\nReduced price : {self.reduced_price}\nLink : {self.link}\n"


def clickElement(driver, xpath):
    try:
        element = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable(
                (By.XPATH, xpath)))
        print("Will click element")
        element.click()
        return 0
    except:
        print("Last page reached or element not clickable")
        return -1

def convertPrice(price):
    if (price.find('.') != -1):
        it = price.find('.')
        price = price[:it] + price[it + 1:]
    return float(price) / 100


def request2BfSoupObj(url_path):
    page = requests.get(url_path)
    print("\nRequesting Page URL: {}\n".format(url_path))
    if page.status_code == 200:
        print("\nRequest OK: Status code {}\n".format(page.status_code))
    else:
        print("\nError with the request:response: {}\n".format(page.status_code))
        raise ConnectionError("\nError with the request:response: {}\n".format(page.status_code))
        return 0
    page.encoding = 'ISO-885901'
    soup = BeautifulSoup(page.text, 'html.parser')  # using the html parser, easier to search in browser
    return soup


def getNextPage(pageSoups):
    nextPageLink = None
    if pageSoups.get('href'):
        nextPageLink = pageSoups['href']
    return nextPageLink


def gen_report_file(listOfItems, scraperType, columns, root_path):
    df = pd.DataFrame(listOfItems, columns=columns)

    while True:
        tmp_file_name = "{}_{}.xlsx".format(scraperType, random.randint(0, 100000))
        tmp_file_name = os.path.join(root_path, tmp_file_name)
        if not os.path.exists(tmp_file_name):
            path = os.path.join(root_path, tmp_file_name)
            break
    df.to_excel(path)
    print("Finished process for {}".format(scraperType))
    print(path)


# Scrapers
def notinoScraper(urlPath, app_path, category):
    listOfProducts = []
    nextPageLink = urlPath

    driver = webdriver.Chrome("D:\PythonPrograms\chromedriver.exe")
    driver.get(urlPath)
    driver.maximize_window()
    clickElement(driver, '//*[@id="exponea-cookie-compliance"]/div/p/a')
    it = 0
    while True:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Div container <=> our div containing all the products
        divContainer = soup.find('div', class_=productsContainer_divClass)
        for singleProduct in divContainer.find_all('div', class_=productContainer_divClass):
            myProduct = product()
            try:
                myProduct.brand = singleProduct.find('h2', class_=productBrand_h2Class).get_text()
            except:
                print("Element not scrapeable")
            try:
                myProduct.title = singleProduct.find('h3', class_=productTitle_h3Class).get_text()
            except:
                print("Element not scrapeable")
            try:
                myProduct.link = "https://www.notino.ro" + singleProduct.find(class_=productLink_hrefClass)['href']
            except:
                print("Element not scrapeable")
            try:
                myProduct.base_price = singleProduct.find('span', class_=productPrice_spanClass).get_text()
            except:
                print("Element not scrapeable")
            try:
                myProduct.description = singleProduct.find('p', class_=productDescription_pClass).get_text()
            except:
                print("Element not scrapable")
            tempList = [myProduct.title, myProduct.brand, myProduct.description, myProduct.link, myProduct.base_price]
            listOfProducts.append(tempList)
            print(myProduct)
        lastPageFlag = clickElement(driver, nextPage_xPath)
        if(lastPageFlag == -1):
            break
        time.sleep(2)
    gen_report_file(listOfItems=listOfProducts,
                    columns=['title', 'brand', 'description', 'link', 'base_price'],
                    scraperType="notino_"+category, root_path=app_path)


notinoScraper("https://www.notino.ro/cosmetice/ingrijirea-parului/", os.getcwd(), "ingrijirea-parului")
