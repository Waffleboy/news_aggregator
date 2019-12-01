#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 12:49:14 2018

@author: waffleboy
"""


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd
import datetime
from selenium.webdriver.chrome.options import Options  

chrome_options = Options()  
chrome_options.add_argument("--headless")  

default_url = "https://www.nea.gov.sg/media/news"

def scrape(url = default_url, given_date = None, override = False):
    driver = load_driver()
    driver.get(url)
    
    # just wait till page load
    element = WebDriverWait(driver, 10).until(
    lambda x: x.find_element_by_class_name('col-md-4'))
    
    first_entry = get_first_elem_of_table(driver)
    date_of_news = parse_date_and_identify(first_entry.text)
    if should_scrape(date_of_news, given_date) or override:
        title, current_url = scrape_entry(driver,first_entry)
        return (title,date_of_news,current_url)
    return

def scrape_entry(driver,elem):
    elem.click()
    current_url = driver.current_url
    title = get_news_title(driver)
    return title, current_url

def get_news_title(driver):
    elem = driver.find_element_by_class_name('advisory-title')
    return elem.text

def load_driver():
    global chrome_options
    return webdriver.Chrome(chrome_options=chrome_options)

def get_first_elem_of_table(driver):
    elem = driver.find_element_by_class_name('col-md-4')
    return elem

def should_scrape(article_date,given_date):
    if given_date == None:
        given_date = datetime.date.today()
    if given_date == article_date:
        return True
    return False
    
def parse_date_and_identify(text):
    date_filtered = text.split('\n')[1] # second element
    parsed_date = datetime.datetime.strptime(date_filtered,'%d %b %Y')
    return parsed_date.date()
    
def test_case():
    return scrape(override=True)
