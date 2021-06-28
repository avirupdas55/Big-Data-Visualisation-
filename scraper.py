# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 15:54:53 2021

@author: avirupdas
"""

#importing packages
import time
import pandas as pd
import re
from google_play_scraper import app, permissions
from selenium import webdriver

# List all the links of pages from which you want to scrape the app-data 
game=['https://play.google.com/store/apps/collection/cluster?clp=ogo1CAESC0dBTUVfQUNUSU9OGhwKFnJlY3NfdG9waWNfdEpjSnhIaXp3TlUQOxgDKgIIB1ICCAI%3D:S:ANO1ljKEF6Y&gsr=CjiiCjUIARILR0FNRV9BQ1RJT04aHAoWcmVjc190b3BpY190SmNKeEhpendOVRA7GAMqAggHUgIIAg%3D%3D:S:ANO1ljLwkfM&hl=en',
      'https://play.google.com/store/apps/collection/cluster?clp=ogoaCAESDkhPVVNFX0FORF9IT01FKgIIB1ICCAE%3D:S:ANO1ljI61gs&gsr=Ch2iChoIARIOSE9VU0VfQU5EX0hPTUUqAggHUgIIAQ%3D%3D:S:ANO1ljJ-4CI',
      'https://play.google.com/store/apps/category/LIBRARIES_AND_DEMO',
      'https://play.google.com/store/apps/collection/cluster?clp=ogoVCAESCVBBUkVOVElORyoCCAdSAggB:S:ANO1ljKni9M&gsr=ChiiChUIARIJUEFSRU5USU5HKgIIB1ICCAE%3D:S:ANO1ljJzQHA',
      'https://play.google.com/store/apps/collection/cluster?clp=ogo8CAESEk5FV1NfQU5EX01BR0FaSU5FUxocChZyZWNzX3RvcGljX25XbUp1bWctVkJ3EDsYAyoCCAdSAggC:S:ANO1ljJZ5Lo&gsr=Cj-iCjwIARISTkVXU19BTkRfTUFHQVpJTkVTGhwKFnJlY3NfdG9waWNfbldtSnVtZy1WQncQOxgDKgIIB1ICCAI%3D:S:ANO1ljJj3pU',
      'https://play.google.com/store/apps/collection/cluster?clp=0g4bChkKE3RvcGdyb3NzaW5nX01FRElDQUwQBxgD:S:ANO1ljL-pGs&gsr=Ch7SDhsKGQoTdG9wZ3Jvc3NpbmdfTUVESUNBTBAHGAM%3D:S:ANO1ljIpVC0',
      'https://play.google.com/store/apps/collection/cluster?clp=ogobCA0SD01VU0lDX0FORF9BVURJTyoCCAdSAggB:S:ANO1ljILh84&gsr=Ch6iChsIDRIPTVVTSUNfQU5EX0FVRElPKgIIB1ICCAE%3D:S:ANO1ljIQkZI']
for ind in range(0,len(game)):
    # Please turn on automation settings for your browser
    
    # for Safari-
    driver = webdriver.Safari(executable_path = '/usr/bin/safaridriver')
    driver.get(game[ind])
    
    # for Chrome- 
    # driver=webdriver.Chrome(ChromeDriveManager().install())
    
    # for Microsoft Edge-
    # // Set the driver path
    # System.setProperty("webdriver.edge.driver", "C://EdgeDriver.exe");
    # // Start Edge Session
    # WebDriver driver = new EdgeDriver();
    
    # Wait for 5 seconds for the page to load
    time.sleep(5)
    
    # Scroll down to the end of page, wait for 3 seconds to load new apps, otherwise proceed to scrape
    SCROLL_PAUSE_TIME=3

    last_height = driver.execute_script("return document.body.scrollHeight")
    time.sleep(SCROLL_PAUSE_TIME)

 
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    time.sleep(SCROLL_PAUSE_TIME)
 
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
 
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
 
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    links_games = []
    elems = driver.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        if "details?id" in elem.get_attribute("href"):
            links_games.append((elem.get_attribute("href")))
        
    links_games = list(dict.fromkeys(links_games))
    header1 = driver.find_element_by_tag_name("h2")

    list_all_elements = []
    for iteration in links_games:
        try:
            driver.get(iteration)
            print(iteration)
            time.sleep(3)
 
            header1 = driver.find_element_by_tag_name("h1")
            star = driver.find_element_by_class_name("BHMmbe")
 
 
            others = driver.find_elements_by_class_name("htlgb")
            list_others = []
            for x in range (len(others)):
                if x % 2 == 0:
                    list_others.append(others[x].text)
 
            titles = driver.find_elements_by_class_name("BgcNfc")
            comments = driver.find_element_by_class_name("EymY4b")
 
            list_elements = [iteration,header1.text, float(star.text.replace(",",".")), comments.text.split()[0]]
            for x in range (len(titles)):
                if titles[x].text == "Descargas":
                    list_elements.append(list_others[x])
                if titles[x].text == "Desarrollador":
                    for y in list_others[x].split("\n"):
                        if "@" in y:
                            list_elements.append(y)
                            break
 
            list_all_elements.append(list_elements)
        except Exception as e:
            print(e)
    
    # Saving the scraped data in a dataframe
    fin=list()
    params=['title', 'description', 'descriptionHTML', 'summary', 'summaryHTML',
           'installs', 'minInstalls', 'score', 'ratings', 'reviews', 'histogram',
           'price', 'free', 'currency', 'sale', 'saleTime', 'originalPrice',
           'saleText', 'offersIAP', 'inAppProductPrice', 'size', 'androidVersion',
           'androidVersionText', 'developer', 'developerId', 'developerEmail',
           'developerWebsite', 'developerAddress', 'privacyPolicy',
           'developerInternalID', 'genre', 'genreId', 'icon', 'headerImage',
           'screenshots', 'video', 'videoImage', 'contentRating',
           'contentRatingDescription', 'adSupported', 'containsAds', 'released',
           'updated', 'version', 'recentChanges', 'recentChangesHTML', 'comments',
           'editorsChoice', 'appId', 'url']
    perm= ['Wi-Fi connection information', 'Other', 'Uncategorized',
           'Photos/Media/Files', 'Storage', 'Microphone', 'Device ID & call information',
           'Phone', 'Device & app history', 'Location', 'Camera', 'Contacts', 'Identity']
    data=pd.DataFrame(columns =params)
    data1=pd.DataFrame(columns =perm)
    
    for i in list_all_elements:
        fin.append(re.split('id=', i[0])[-1])
        temp=app(fin[-1],lang='en',country='in')   # set default language as English and region as India
        data = data.append(temp,ignore_index = True)
        data1 = data1.append(permissions(fin[-1],lang='en',country='in'),ignore_index = True)
    
    # concatenating the usual data and app permissions
    fin_dat=pd.concat([data,data1],axis=1)
    fin_dat.to_csv('file'+str(ind+1)+'.csv')
    driver.quit()


