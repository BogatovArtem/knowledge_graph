RESOURS = ["http://sci-hub.se"]
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
browser = webdriver.Chrome()
# Скачиваем статью через selenium
def save_article(doi):

    browser.get('http://sci-hub.se/' + doi)

    # WTF ?
    try:
        browser.find_element_by_xpath("""/html/body/div[1]/div[1]/ul/li[2]/a""").click()
    except:
        try:
            browser.find_element_by_css_selector("#buttons > ul > li:nth-child(2) > a").click()
        except:
            ""

# Скачиваем статью через selenuim по названию
def save_article_name(name):

    browser.get(RESOURS[0])
    input_filed = browser.find_element_by_xpath("""/html/body/div[1]/div[4]/form/input[2]""")
    input_filed.send_keys(name)
    input_filed.send_keys(Keys.ENTER)