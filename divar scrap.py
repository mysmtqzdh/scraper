import pandas as pd
import requests
import time
import wget
from bs4 import BeautifulSoup
from arabic_reshaper import reshape
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_binary
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager



options = Options()
options.add_argument("start-maximized")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('log-level=3')
options.add_argument("headless");

# variables
url = 'https://divar.ir/s/tehran/refrigerator-freezer/like-new?status=used%2Crepair-needed&has-photo=true&non-negotiable=true&exchange=exclude-exchanges'

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# You can set your own pause time. My laptop is a bit slow so I use 1 sec
scroll_pause_time = 1
screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web
i = 1
data = []


driver.maximize_window()
driver.get(url)
timeout = 5


while True:

    products = driver.find_elements(by=By.XPATH, value="//div[@class='post-card-item kt-col-6 kt-col-xxl-4'] ")
    for x in products:
        purl = x.find_element(By.CSS_SELECTOR, value="a.kt-post-card").get_attribute("href")
        pname = x.find_element(By.CSS_SELECTOR, value="div.kt-post-card__title",).text
        price = x.find_element(By.CSS_SELECTOR, value="div.kt-post-card__description").text
        location = x.find_element(By.CSS_SELECTOR, value="span.kt-post-card__bottom-description").text
        soup = BeautifulSoup(requests.get(purl).content, "html.parser")
        pdesc = soup.find("p" ,class_="kt-description-row__text").text
        imgurl1 = soup.find('meta' , attrs={"property" : "og:image"})['content'].replace("webp", "jpg")
        imgurl2 = imgurl1.replace(".jpg", ".1.jpg")
        if [purl, pname, price, pdesc, location, imgurl1, imgurl2] not in data:
            data.append([purl, pname, price, pdesc, location, imgurl1, imgurl2])   
            filename1 = wget.download(imgurl1, out="./images")
            try:
                
                filename2 = wget.download(imgurl2, out="./images")
            except:
                pass
                    
            
        else:
            continue

    # scroll one screen height each time
    driver.execute_script(
        "window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
    i += 1
    time.sleep(scroll_pause_time)
    # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
    scroll_height = driver.execute_script("return document.body.scrollHeight;")

    print(len(data))
    if len(data) >= 200: ######### input data length ############### 
        driver.close()
        break


df = pd.DataFrame(data, columns=['Product URL', 'Name', 'Price', 'Description', 'Location', 'Img URL1', 'Img URL2'])
df.to_excel("example.xlsx")
