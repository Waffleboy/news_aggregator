#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 23:53:31 2018

@author: waffleboy
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import logger_settings
import datetime
import news_api
# Enable logging
logger = logger_settings.setupLogger().getLogger(__name__)


#==============================================================================
# SETTINGS
#==============================================================================
# if True, when bot begins for the first time, itll get all the news for the
# past month.
RUN_ONE_TIME_AGGREGATION = True
CHANNEL_ID = "@neatnews"

#==============================================================================
#                               SLASH COMMANDS
#==============================================================================

START_MSG = """
    Hi, I aggregate news about NEA.
    
    /refresh - fetches latest (24hr) news
"""

def helpme(bot, update):
    update.message.reply_text(getHelpText())

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))
    
def start(bot, update):
    update.message.reply_text(START_MSG)

def refresh(bot,update):
    res = obtain_news()
    update.message.reply_text(res)
    return

#==============================================================================
#                           Recurring jobs
#==============================================================================

def daily_news(bot, job):
    text = obtain_news()
    send_news_to_channel(bot,text)
                      

def monthly_news(bot,job):
    text = obtain_news(date_range=_month_ago_date())
    send_news_to_channel(bot,text,monthly=True)
    
#==============================================================================
#                               Helper Funcs
#==============================================================================

## main api call for news. 
# date_range: <str> date format YYYY-MM-DD or 'yesterday' or None
def obtain_news(query = "NEA Singapore",date_range = 'yesterday',\
                format_str = True):
    
    if date_range == 'yesterday': #convert for auto processing
        date_range = _yesterday_date()
    news = news_api.query_api(query,date_range)
    if format_str:
        return format_news_api_results(news)
    return news

# takes in text and formats it correctly to send to telegram channel
def send_news_to_channel(bot,text,monthly = False):
    global CHANNEL_ID
    text_fluff = add_fluff_to_news_string(text,monthly)
    ## HACK: Fix too long message length
    text_chunks = message_length_fixer(text_fluff)
    for chunk in text_chunks:
        restored_text = '\n\n'.join(chunk)
        bot.send_message(chat_id=CHANNEL_ID,text=restored_text)
    return


def _yesterday_date():
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    return yesterday_str

def _month_ago_date():
    month_ago = datetime.datetime.today() - datetime.timedelta(days=30)
    month_ago_str = month_ago.strftime('%Y-%m-%d')
    return month_ago_str

def add_fluff_to_news_string(news_str,monthly):
    date = datetime.date.today().strftime('%d %b %Y')
    if monthly:
        fluff = "NEA News for the last 30 days:\n\n"
    else:
        fluff = "NEA News for {}:\n\n".format(date)
    return fluff + news_str

def format_news_api_results(res):
    s = ''
    for i,entry in enumerate(res):
        temp = "{}. {}\n{}\n\n".format(i+1,entry['title'],entry['url'])
        s += temp
    return s

def getHelpText():
    return START_MSG

def message_length_fixer(text):
    # split every 10 messages.
    text_split = text.split('\n\n')
    text_chunks = list(chunks(text_split,10))
    return text_chunks
    
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
    
#==============================================================================
#                                   Misc
#==============================================================================

# Standard reply upon texting the bot
def standardReply():
    s = "At the moment, I only reply to slash commands. Please try /help for more information!"
    return s

def isProductionEnvironment():
    # temp
    return True
    if os.environ.get('PRODUCTION'):
        return True
    return False
    
def getUpdater():
    if isProductionEnvironment():
        logger.info("Using Production key")
        return Updater(os.environ.get("NEA_NEWS_BOT"))
    return Updater(os.environ.get("NEA_NEWS_BOT"))

#==============================================================================
#                                   Run
#==============================================================================
    
def main():
    global CHANNEL_ID
    logger.info("Starting NEAWs Bot")
    # Create the EventHandler and pass it your bot's token.
    updater = getUpdater()

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", helpme))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("refresh", refresh))
    
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, standardReply()))

    # log all errors
    dp.add_error_handler(error)
    
    # get job queue
    j = updater.job_queue

    # Start the Bot
    updater.start_polling()
    
    if RUN_ONE_TIME_AGGREGATION:
        updater.bot.send_message(CHANNEL_ID,"Aggregation set to ON: Beginning one-time monthly news collation.\n")
        j.run_once(monthly_news,0)
    news_job = j.run_repeating(daily_news, interval=60*60*24, first=0)

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
