from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import Column, String, Text, create_engine, MetaData, Table
import datetime


def main():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    browser = webdriver.Chrome(executable_path='webdriverChrome/chromedriver.exe')
    browser.get(f"https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-1000/c37l1700273")
    WebDriverWait(browser, 60).until(
        EC.visibility_of_any_elements_located((By.CLASS_NAME, "pagination")))
#############################################
#   Create tables
    engine = create_engine('mysql+mysqlconnector://root:1234@localhost/apart', echo=True)
    meta = MetaData(engine)
    conn = engine.connect()
    image_sql = Table('image', meta, Column('image', Text))
    title_sql = Table('title', meta, Column('title', String(250)))
    date_sql = Table('date', meta, Column('date', Text))
    location_sql = Table('location', meta, Column('location', String(250)))
    bedroom_sql = Table('bedroom', meta, Column('bedroom', String(250)))
    descriptions_sql = Table('descriptions', meta, Column('descriptions', Text))
    price_sql = Table('price', meta, Column('price', String(250)))
    meta.create_all()

    def pagination():
        pagin = browser.find_element(By.CLASS_NAME, 'pagination').find_element(By.CLASS_NAME, 'selected').text
        pagin = int(pagin) - 1
        browser.get(f"https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{pagin}/c37l1700273")
        if pagin >= 1:
            settings()
        else:
            print('Complete')
            browser.quit()

    def image():
        link_image = browser.find_elements(By.TAG_NAME, 'img')
        for link in link_image:
            find_url = link.get_attribute('data-src')
            if find_url is not None:
                conn.execute(image_sql.insert().values(image=find_url))

    def titles():
        title = browser.find_elements(By.CSS_SELECTOR, 'div.title')
        for item in title:
            conn.execute(title_sql.insert().values(title=item.text))

    def date():
        date_posted = browser.find_elements(By.CLASS_NAME, 'date-posted')
        for dates in date_posted:
            if dates.text.find('ago') != -1:
                date_now = datetime.date.today()
                conn.execute(date_sql.insert().values(date=date_now.strftime('%d/%m/%Y')))
            else:
                conn.execute(date_sql.insert().values(date=dates.text))

    def locations():
        location = browser.find_elements(By.CLASS_NAME, 'location')
        for item in location:
            local = item.find_element(By.TAG_NAME, 'span').text
            conn.execute(location_sql.insert().values(location=local))

    def bedroom():
        bedrooms = browser.find_elements(By.CLASS_NAME, 'bedrooms')
        for bed in bedrooms:
            conn.execute(bedroom_sql.insert().values(bedroom=bed.text[5:]))

    def descriptions():
        description = browser.find_elements(By.CLASS_NAME, 'description')
        for desc in description:
            conn.execute(descriptions_sql.insert().values(descriptions=desc.text))

    def prices():
        price = browser.find_elements(By.CLASS_NAME, 'price')
        for item in price:
            conn.execute(price_sql.insert().values(price=item.text))

    def settings():
        image()
        titles()
        date()
        locations()
        bedroom()
        descriptions()
        prices()
        pagination()

    settings()


if __name__ == "__main__":
    main()
