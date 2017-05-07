from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import multiprocessing as mp
from selenium.common.exceptions import NoSuchElementException
import string
import robotparser
import re

url = "http://ritasbreck.com/"


def checkUrl(url): #make sure a valid url has been entered
    if url[:4] == "http":
        intLinks = []
        extLinks = [] 
        mailAdds = []
        ogextLinks = []
        counter = 0
        numOfextLinks = 0
        i = 0

        driver1 = webdriver.Remote(
        command_executor='http://127.0.0.1:4444/wd/hub',
        desired_capabilities=DesiredCapabilities.PHANTOMJS)
        startProcess(url, intLinks, extLinks, mailAdds, driver1, counter, ogextLinks, numOfextLinks, i)
    else:
        print("url address must begin with http or https")
        return


def seoaPass(url):

    robotsUrl = re.findall(r'.*[.][a-zA-Z]+', url)
    robotsUrl = str(robotsUrl[0])
    robotsUrltxt = robotsUrl + '/robots.txt'
    rp = robotparser.RobotFileParser()
    rp.set_url(robotsUrltxt)    
    rp.read()

      
    if rp.can_fetch('*', url) == True:
        
        return True
    else:
        return False
       
def startProcess(url, intLinks, extLinks, mailAdds, driver1, counter, ogextLinks, numOfextLinks, i): # returns all internal and external url's
    robotsUrl = re.findall(r'.*[.][a-zA-Z]+', url)
    robotsUrl = str(robotsUrl[0])
    
    numOfLetters = len(robotsUrl)
    print("startProcess    " + url)
    for item in extLinks:
        print(item)
    if seoaPass(url) == True:
        print("robots allowed")
        driver1.get(url)
        
        links = driver1.find_elements_by_tag_name('a')
        for link in links:
            link = link.get_attribute("href")
            robotsLink = re.findall(r'.*[.][a-zA-Z]+', link)
            robotsLink = str(robotsLink)
            if link[:numOfLetters] == robotsUrl and link not in intLinks:
                intLinks.append(link)
            elif link[:numOfLetters] != robotsUrl and link[:4] == "http" and link not in extLinks:
                extLinks.append(link)
            elif link[:6] == "mailto" and link not in mailAdds:
                mailAdds.append(link)
            else:
                pass    
        parseIntLinks(url, intLinks, extLinks, mailAdds, driver1, numOfLetters, counter, ogextLinks, numOfextLinks, i)
    else:
        print("sorry access by seoabot is dissalowed by this website") 
        


def parseIntLinks(url, intLinks, extLinks, mailAdds, driver1, numOfLetters, counter, ogextLinks, numOfextLinks, i):
    robotsUrl = re.findall(r'.*[.][a-zA-Z]+', url)
    robotsUrl = str(robotsUrl[0])
    print("second process   " + url)
    ogintLinks = list(intLinks)
    for item in extLinks:
        print(item)
    for link in ogintLinks:

        if seoaPass(link) == True:
            driver1.get(link)
            
            onelayerIntLinks = driver1.find_elements_by_tag_name('a')
            for onelayerIntLink in onelayerIntLinks:
                onelayerIntLink = onelayerIntLink.get_attribute("href")
                robotsLink = re.findall(r'.*[.][a-zA-Z]+', url)
                robotsLink = str(robotsLink)
                if onelayerIntLink == None:
                    break
                elif onelayerIntLink[:numOfLetters] == robotsUrl and onelayerIntLink not in intLinks:
                    intLinks.append(onelayerIntLink)
                    
                elif onelayerIntLink[:numOfLetters] != robotsUrl and onelayerIntLink[:4] == "http" and onelayerIntLink not in extLinks:
                    extLinks.append(onelayerIntLink)

                elif re.match(r'@', onelayerIntLink) and onelayerIntLink[:6] == "mailto" and onelayerIntLink is not None and onelayerIntLink not in mailAdds:

                    mailAdds.append(onelayerIntLink)

                else:
                    pass
        else:
            print("seoabot is dissallowed to visit this link by the robots.txt")
            
            pass
    parseExtLinks(url, intLinks, extLinks, mailAdds, driver1, numOfLetters, counter, ogextLinks, numOfextLinks, i)      
    

def parseExtLinks(url, intLinks, extLinks, mailAdds, driver1, numOfLetters, counter, ogextLinks, numOfextLinks, i):
    print("third process " + url)
    for item in extLinks:
        print(item)
    if counter == 0:
        ogextLinks = list(extLinks)
        counter = 1
        numOfextLinks = len(ogextLinks)


    

    
    for i in range(numOfextLinks):
        link = ogextLinks[i]
        
        if seoaPass(link) == True:
            
            print("robots allowed2")
            
            startProcess(link, intLinks, extLinks, mailAdds, driver1, counter, ogextLinks, numOfextLinks, i)
            
           
        else:
            print("seoabot is dissallowed to visit this link by the robots.txt")
            
            pass
    print(intLinks)
    print(extLinks)
    print(mailAdds)
    driver1.close
    exit()  

        


if __name__ == '__main__':
    checkUrl(url)







