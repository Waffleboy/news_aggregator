#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 23:31:38 2018

@author: waffleboy
"""

from newsapi import NewsApiClient
import os

# Init
newsapi = NewsApiClient(api_key=os.environ["GOOGLE_NEWS"])

def query_api(query_str,date_range = None):
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
