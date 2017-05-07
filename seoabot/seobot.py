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
        numOfLetters = len(url)
        driver1 = webdriver.Remote(
        command_executor='http://127.0.0.1:4444/wd/hub',
        desired_capabilities=DesiredCapabilities.PHANTOMJS)
        startProcess(url, intLinks, extLinks, mailAdds, driver1, numOfLetters)
    else:
        print("url address must begin with http or https")
        return


def seoaPass(url): #regex url to stop after .com/robots.txt and check robots text
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
       
def startProcess(url, intLinks, extLinks, mailAdds, driver1, numOfLetters): # returns all internal and external url's
    

    if seoaPass(url) == True:
        print("robots allowed")
        driver1.get(url)
        
        links = driver1.find_elements_by_tag_name('a')
        for link in links:
            link = link.get_attribute("href")
            
            if link[:numOfLetters] == url and link not in intLinks:
                intLinks.append(link)
                print(link)
            elif link[:numOfLetters] != url and link[:4] == "http" and link not in extLinks:
                print(link)
                extLinks.append(link)
            elif link[:6] == "mailto" and link not in mailAdds:
                mailAdds.append(link)
                print(link)
            else:
                pass    
        
        
        parseIntLinks(url, intLinks, extLinks, mailAdds, driver1, numOfLetters)
    else:
        print("sorry access by seoabot is dissalowed by this website") 
    


def parseIntLinks(url, intLinks, extLinks, mailAdds, driver1, numOfLetters):
    ogintLinks = list(intLinks)
    
    for link in ogintLinks:

        if seoaPass(link) == True:
            driver1.get(link)
            
            onelayerIntLinks = driver1.find_elements_by_tag_name('a')
            for onelayerIntLink in onelayerIntLinks:
                onelayerIntLink = onelayerIntLink.get_attribute("href")
                
                if onelayerIntLink == None:
                    break
                elif onelayerIntLink[:numOfLetters] == url and onelayerIntLink not in intLinks:
                    intLinks.append(onelayerIntLink)
                    print("driver url!!!!!!!!!!!!!!!")
                    print(link)
                    print(onelayerIntLink)
                elif onelayerIntLink[:numOfLetters] != url and onelayerIntLink[:4] == "http" and onelayerIntLink not in extLinks:
                    extLinks.append(onelayerIntLink)
                    print("driver url!!!!!!!!!!!!!!!")
                    print(link)
                    print(onelayerIntLink)
                elif re.match(r'@', onelayerIntLink) and onelayerIntLink[:6] == "mailto" and onelayerIntLink is not None and onelayerIntLink not in mailAdds:
                    print(onelayerIntLink)
                    mailAdds.append(onelayerIntLink)

                else:
                    pass
        else:
            print("seoabot is dissallowed to visit this link by the robots.txt")
    driver1.close
    exit()
    parseExtLinks(url, intLinks, extLinks, mailAdds, driver1, numOfLetters)      
    

def parseExtLinks(url, intLinks, extLinks, mailAdds, driver1, numOfLetters): 
    ogextLinks = list(extLinks)
    intLinks = []
    extLinks = [] 
    mailAdds = []
    returnd = {}
    for link in ogextLinks:
 
        
        if seoaPass(link) == True:
            print("robots allowed")
            startProcess(url, intLinks, extLinks, mailAdds, driver1, numOfLetters):
            driver1.get(link)
            links = driver1.find_elements_by_tag_name('a')
            for link in links:
                link = link.get_attribute("href")
            
                if url == robotsUrl and link not in returnd.values():
                    intLinks.append(link) #follow internals search for original url !##############################################
                    returnd['trusted'] = link
                elif link[:numOfLetters] == robotsUrl and link not in intLinks:
                    intLinks.append(link)                    
                    robotsUrl = re.findall(r'.*[.][a-zA-Z]+', link)
                    robotsUrl = str(robotsUrl[0])
                    print("here")
                    print(robotsUrl)
                    print(url)
                    robotsUrltxt = robotsUrl + '/robots.txt'
                    rp = robotparser.RobotFileParser()
                    rp.set_url(robotsUrltxt)    
                    rp.read()
                    if rp.can_fetch('*', link) == True:
                        driver1.get(link)

                else:
                    pass    
        else:
            print("seoabot is dissallowed to visit this link by the robots.txt")
    print(intLinks)
    print(extLinks)
    print(mailAdds)
    driver1.close
    exit()  

        


if __name__ == '__main__':
    checkUrl(url)







