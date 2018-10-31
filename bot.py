#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 23:53:31 2018

@author: waffleboy
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import logger_settings
import news_api
# Enable logging
logger = logger_settings.setupLogger().getLogger(__name__)

START_MSG = """
    Hi, I aggregate news about NEA.
    
    /refresh - fetches latest (24hr) news
"""
#==============================================================================
#                               SLASH COMMANDS
#==============================================================================
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
#                           Recurring queues
#==============================================================================

def daily_news(bot, job):
    bot.send_message(chat_id='@neatnews', 
                      text=obtain_news())


#==============================================================================
#                               Helper Funcs
#==============================================================================

def obtain_news(query = "NEA Singapore"):
    news = news_api.query_api(query)
    res = format_news_api_results(news)
    return res

def format_news_api_results(res):
    s = ''
    for i,entry in enumerate(res):
        temp = "{}. {}\n{}\n\n".format(i+1,entry['title'],entry['url'])
        s += temp
    return s

def getHelpText():
    return START_MSG
    
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
    
    news_job = j.run_repeating(daily_news, interval=60*60*24, first=0)

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
