import os, requests, re, logging
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

# loggers
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8443'))

# Repalce <TOKEN> with your own Telegram API Token
token = '<TOKEN>'

# Selenium Setup (Heroku Compatible)
CHROMEDRIVER_PATH = "/app/.chromedriver/bin/chromedriver"
chrome_bin = os.environ.get('GOOGLE_CHROME_SHIM', "chromedriver")
options = ChromeOptions()
options.binary_location = chrome_bin

def go(bot, update):
    driver = webdriver.Chrome(executable_path="chromedriver", chrome_options=options)

    # Get the message from Useer
    m = update.message.text
    if ' to ' not in m:
        update.message.reply_text('Please enter two locations, Example: Toa Payoh to Jurong West')
    else:
        # a - from location
        a = m.split(' to ')[0]
        a = a.replace(' ', '%20')

        # b - to location
        b = m.split(' to ')[1]
        b = b.replace(' ', '%20')

        # Contruct URL
        url = 'https://gothere.sg/maps#q:{}%20to%20{}'.format(a, b)
        
        # Start of Selenium
        driver.get(url)
        
        # xpath for route info
        route_infos_xpath = '//*[@id="ds"]/div[2]/p'
        route_infos = driver.find_elements_by_xpath(route_infos_xpath)
        
        # Assigning list for end result
        info = []
        
        for route_info in route_infos:
          info.append(route_info.text)
         
        reply = "" #start of reply adding
        reply += "<b>Total Duration: {}\nTotal Price: {}\nTotal Transfer: {}</b>\n\n".format(info[0],info[1],info[2])
        
        journeys_xpath = '//*[@id="d"]/li'
    
        journeys = driver.find_elements_by_xpath(journeys_xpath)
        
        count = 1
        for journey in journeys:
            raw = journey.text
            
            texts = raw.split('\n')
            
            # Manual Text Processing
            if '+' in texts[1]:
                if 'Line' in texts[2]:
                    text = '&#x1f686 ' + texts[2] + ' &#x1f686' + '\n'
                elif 'Bus' in texts[2]:
                    text = '&#x1f68d '  + texts[2] + ' &#x1f68d' + '\n'
                text += '\t\t\t\t\t\t\t\t\t' + " ".join(texts[0:2]).lower()
                text += ' (waiting time)' + '\n'
                text += '\t\t\t\t\t\t\t\t\t' + texts[3]
                
            else:
                if 'Walk' in texts[1]:
                    text =  '&#x1f6b6 ' +  texts[1] +  ' &#x1f6b6' + '\n'
                else:
                    text = texts[1] + '\n' 
                text += '\t\t\t\t\t\t\t\t\t' + texts[0].lower() + '\n'
                
                text += '\t\t\t\t\t\t\t\t\t' + texts[2]
                    
            reply += '<b>' + str(count) + ' | </b>'  + text + "\n\n"
            count+=1
            
        update.message.reply_text(reply, parse_mode = 'HTML')
        
        # Shut down Selenium
        driver.close()
    
    
def start(bot,update):
    update.message.reply_text("Hi there! I'm your friendly Journey Bot KJB\U0001F60A")


def main():
    updater = Updater(token)
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=token)
    
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text,go))
    dp.add_handler(CommandHandler('start',start))

    # Repalce <HEROKU URL> with your own Heroku URL
    updater.bot.set_webhook("<HEROKU_URL>" + token)
    
    updater.idle()

if __name__ == '__main__':
    print ('Bot is running')
    main()
    print ('Bot ending')