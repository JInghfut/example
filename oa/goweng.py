import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


with open(r'url.json') as f:
    a=f.readline()
print a
dict_a=json.loads(a)
url_list=[x['pcUrl'] for x in dict_a['body']['pendingList']]
print len(url_list)



driver =  webdriver.Chrome('C:\\chromedriver\\chromedriver.exe')
#driver =  webdriver.Firefox()
#driver.maximize_window()

driver.get("")
cookies = driver.get_cookies()
#
driver.delete_all_cookies()

#for cookie in cookies :
driver.add_cookie({
      'domain': '', # note the dot at the beginning
      'name': 'JSESSIONID',
      'value': '',
      'path': '',
      'expires': None
    })

startTime = time.time()
for url in url_list:
    driver.get(url)
    #str='''//*[@id="toolbar"]/button[2]/span'''
    # searchbox = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH ,str)))
    # searchbox.click()
    time.sleep(6)
    windows_before = driver.window_handles
    driver.find_element_by_xpath('''//*[@id="toolbar"]/button[2]/span''').click()
    time.sleep(2)

    iframe = driver.find_elements_by_tag_name('iframe')[0]
    driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
    driver.execute_script("$('#layui-layer12').contents().find('#okbtn').click();")
    driver.execute_script("$('#layui-layer12').find('#okbtn').click(function(){alert(1)});")
    str='''//*[@id="okbtn"]'''
    searchbox = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH ,str)))
    print driver.page_source
    driver.find_element_by_xpath('''//*[@id="okbtn"]''').click()
    time.sleep(2)
endTime= time.time()
print (endTime-startTime)
#display.stop()