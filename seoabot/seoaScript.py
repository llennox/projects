from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import multiprocessing as mp
from selenium.common.exceptions import NoSuchElementException
import string
import robotexclusionrulesparser
import re
import time

url = "http://www.baezmedia.org/"




def checkUrl(url): #make sure a valid url has been entered
    if url[:4] == "http" and url.endswith('/'):
        return True
    else:
        print("url address must begin with http or https and end in /")
        return False

def seoaPass(url):
    robotsUrl = re.findall(r'.*[.][a-zA-Z]{2,3}', url)
    
    robotsUrl = str(robotsUrl[0])
    
    robotsUrltxt = robotsUrl + '/robots.txt'
    rerp = robotexclusionrulesparser.RobotExclusionRulesParser()
    try:
        rerp.fetch(robotsUrltxt)
        if rerp.is_allowed("seoabot/0.9 selenium webdriver, see http//:seoabot.com", url):
            return True
        else:
            print(url + "      :disallow")
            return False
    except:
        return False

def strainUrl(url, extList, intList, mailtoList, blockedList, currIntUrl):
    driver1 = webdriver.Remote(
    command_executor='http://127.0.0.1:4444/wd/hub',
    desired_capabilities=DesiredCapabilities.PHANTOMJS)
    if checkUrl(url) == True and seoaPass(url) == True:
        robotsUrl = re.findall(r'.*[.][a-zA-Z]+[\/]', currIntUrl)
        if robotsUrl is not None:
            robotsUrl = str(robotsUrl[0])
            
        
        if currIntUrl == 'https://twitter.com/':
            return
        driver1.get(url)
        print("getting" + url)
        links = driver1.find_elements_by_tag_name('a')
        for link in links:
            
            link = link.get_attribute("href")
          
            if link is not None and link[:4] == "http" and seoaPass(link) == True:

                robotsLink = re.findall(r'.*[.][a-zA-Z]+[\/]', link)
                if robotsLink is not None:
                    robotsLink = str(robotsLink[0])
                if link is not None and robotsLink == robotsUrl and link not in intList:
                    
                    intList.append(link)
                elif link is not None and robotsLink != robotsUrl and link not in extList and link[:4] == "http":
                    extList.append(link)
                   

                elif link is not None and link[:6] == "mailto" and link not in mailtoList:
                    mailtoList.append(link)
                else:
                    continue
            
            else:
                if link == None:
                    continue
                else:
                    blockedList.append(link)
        
        driver1.close
        return                
    else:
        blockedList.append(url)
        driver1.close
        return 

def controller(url):
    ogurl = re.findall(r'.*[.][a-zA-Z]+[\/]', url)
    extList = []
    intList = []
    mailtoList = []
    blockedList = []
    backlinkList = []
    nobacklinkList = []
    disList = []
    workingd = {}
    counter = 1
    counter1 = 1
    for i in range(0, 3):
        if i == 0:
            currIntUrl = url
            strainUrl(url, extList, intList, mailtoList, blockedList, currIntUrl) 
            ogintList = list(intList)
        elif i == 1:
            mytime = time.clock() + 0.001
            print(mytime)
            for item in ogintList:
                if mytime <= time.clock():
                    print("worked")
                    break
                print(time.clock())
                url = item                      
                strainUrl(url, extList, intList, mailtoList, blockedList, currIntUrl)
                print("1")
               
            ogextList = list(extList)
        elif i == 2:#erase some of the lists further functions inside this for loop!!!!!
            intList = []
            extList = []
            mailtoList = [] 
            blockedList = []
             
            nogextList = []
            for item in ogextList:
                robotsUrl = re.findall(r'.*[.][a-zA-Z]+[\/]', item)
                robotsUrl = str(robotsUrl[0])
                if robotsUrl not in nogextList:
                    nogextList.append(robotsUrl)
            print(nogextList)
            blockedList = []
            for item1 in nogextList:
                 
                 url = item1
                 
                 currIntUrl = url
                 strainUrl(url, extList, intList, mailtoList, blockedList, currIntUrl)
                 ogintList = list(intList)
                 mytime = time.clock() + 0.001
                 for item in ogintList:
                     if mytime <= time.clock():
                         print("worked")
                         break
                     else:
                         url = item
                         currIntUrl = url
                         strainUrl(url, extList, intList, mailtoList, blockedList, currIntUrl)
                     ## i can move this if it gets too big
                         print(blockedList)
                         
                     for litem in extList:
                         litem = re.findall(r'.*[.][a-zA-Z]+[\/]', litem)
                 
                         print("last hook")
                         if litem == ogurl and item1 not in backlinkList:
                             mycounter = 'backlink'
                             backlinkList.append(item1)
                             mycounter = mycounter + str(counter)
                             workingd[mycounter] = item1
                             counter += 1
                             
                         elif item1 not in nobacklinkList: 
                             nobacklinkList.append(item1)
                             mycounter1 = 'no-backlink'
                             mycounter1 = mycounter1 + str(counter1)
                             workingd[mycounter1] = item1
                             counter1 += 1
                         else:
                             continue
                         
            print(workingd)###just need to add disallow category
            exit()
        else:
            return returnd
    exit()



if __name__ == '__main__':
    controller(url)

#elif i == 2: 
# need to follow (for loop) ext links and repeat (inside step 3) step 1 and 2,,, return a dict with trusting untrusting disallowed attached 







