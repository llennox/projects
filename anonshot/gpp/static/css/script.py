from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Firefox()
driver.get("http://tickets.burningman.org/")
elem = driver.find_element_by_xpath("/html/body/div/div/div/div/div[2]/div/main/article/div/dl/dd/div/ul/li[4]/a")
elem.click()
time.sleep(10)
