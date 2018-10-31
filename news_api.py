#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 23:31:38 2018

@author: waffleboy
"""

from newsapi import NewsApiClient
import datetime
import os

# Init
newsapi = NewsApiClient(api_key=os.environ["GOOGLE_NEWS"])

def _yesterday_date():
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    return yesterday_str



def query_api(query_str,date_range = _yesterday_date()):
    if date_range:
        news = newsapi.get_everything(q=query_str,
                                      language='en',
                                      from_param = date_range,
                                      sort_by='relevancy')['articles']
        return news
    
    return newsapi.get_everything(q=query_str,
                                      language='en',
                                      sort_by='relevancy')['articles']
    
    
    
#==============================================================================
# Other helpers
#==============================================================================
def formatter(res):
    return
