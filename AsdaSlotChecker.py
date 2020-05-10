#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import yagmail
import time
import logging
import sys

# Settings for generating log file
logging.basicConfig(level=logging.INFO, filename='AsdaSlotChecker.log', 
                    filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.info('Application started')

# Setting to make chromedriver not appear automated to avoid trigering Captcha
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options, executable_path=r"/usr/lib/chromium-browser/chromedriver")

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
  "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
  """
})
driver.execute_cdp_cmd("Network.enable", {})
driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browser1"}})

driver.implicitly_wait(60) # Wait 60 seconds for each command execution for webdriver

try:
    driver.get("https://www.asda.com/login")
    login_element = driver.find_element_by_xpath('//*[@id="app"]/main/div/div/div/div/form/button')
    username_element = driver.find_element_by_xpath('//*[@id="app"]/main/div/div/div/div/form/div[1]/div/input')
    password_element = driver.find_element_by_xpath('//*[@id="password"]')

    username = 'Asda login username'
    password = 'Asda password'

    username_element.send_keys(username)
    password_element.send_keys(password)
    login_element.send_keys(Keys.RETURN)
    
    logging.info('Login successful!')

    time.sleep(30) # Wait for 30 seconds before navigating to next page

    driver.get('https://groceries.asda.com/checkout/book-slot?tab=deliver&origin=/')
    nextbutton = driver.find_element_by_xpath('//*[@id="main-content"]/main/div[2]/div[2]/div[2]/div[3]/button')

    # Click Next button several times to load all available delivery slots in the page
    while True:
        try:
            nextbutton.send_keys(Keys.RETURN)
        except:
            break
            
    html = driver.page_source # Save the html with all delivery slots info
    logging.info('Delivery slot information acquired')
    driver.close()

    soup = BeautifulSoup(html, 'html.parser')
    alltimes = soup.find_all(class_ = 'co-slots__time')
    alldates = soup.find_all(class_ = 'co-slots__day')
    allslots = soup.find_all(class_ = 'co-slots__price-content co-slots__price-content--box co-slots__price-content--pointer')

    # Create a matrix/table with all time, date and slot information
    slotmatrix = []
    j = 0
    for i in range (len(alltimes)):
        slotmatrix.append(allslots[j:j+len(alldates)])
        j = j+len(alldates)

    # Extract available slot price, date and time
    availableslots = []
    for time in range (len(slotmatrix)):
        for date in range (len(slotmatrix[time])):
            if slotmatrix[time][date].span != None and slotmatrix[time][date].span.div.text != 'Sold Out':
                availabletime = ' '.join(alltimes[time].text.split())
                availabledate = ' '.join(alldates[date].text.split())
                price = slotmatrix[time][date].span.div.text
                availableslots.append(availabletime + ' - ' + availabledate + ' - ' + price + '\n' )

    logging.info('Available delivery slots: %s', availableslots)

    # If slot is available, send email with the info
    if availableslots:
        sender_email = 'sender gmail address'
        receiver_email = 'receiver gmail address'
        path_to_oauth2 = 'path to oauth file'
        
        yag = yagmail.SMTP(sender_email, oauth2_file=path_to_oauth2)
        yag.send(to=receiver_email, subject='Availabe slots', contents=availableslots)

except:
    logging.exception("Exception occurred")
    sys.exit(1)
