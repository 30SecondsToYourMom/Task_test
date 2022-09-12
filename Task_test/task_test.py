from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import Column, String, Text, create_engine, MetaData, Table
import datetime
# from oauth2client.service_account import ServiceAccountCredentials
# from googleapiclient import discovery
# import os


def main():
    ########################################################
    #   Selenium options
    options = webdriver.ChromeOptions()
    options.headless = True
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
#######################################################
    # #   GoogleSheets
    #
    # scope = ['https://spreadsheets.google.com/feeds',
    #          'https://www.googleapis.com/auth/drive']
    # creds_json = os.path.dirname(__file__) + "/venv/creds/winter-sum-362217-2a7455336a36.json"
    # credentials = ServiceAccountCredentials.from_json_keyfile_name(
    #     creds_json, scope)
    # service = discovery.build("sheets", "v4", credentials=credentials)
    # spreadsheet = service.spreadsheets().create(body={
    #     'properties': {'title': 'apart'},
    #     'sheets': [{'properties': {'sheetType': 'GRID',
    #                                'sheetId': 0,
    #                                'title': 'apart'
    #                                }}]
    # }).execute()
    #
    # service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet['spreadsheetId'], body={
    #     "valueInputOption": "USER_ENTERED",
    #     "data": [
    #         {"range": "apart!A1:G1",
    #          "majorDimension": "ROWS",
    #          "values": [["Link for image", "Title", "Date", "Location", "Bedroom", "Description", "Price"]]}
    #
    #     ]
    # }).execute()
    # #   Google Drive
    # scopeDrive = ['https://www.googleapis.com/auth/drive']
    # credentialsDrive = ServiceAccountCredentials.from_json_keyfile_name(
    #     creds_json, scopeDrive)
    # driveService = discovery.build("drive", "v3", credentials=credentialsDrive)
    # driveService.permissions().create(
    #     fileId=spreadsheet['spreadsheetId'],
    #     body={'type': 'anyone', 'role': 'reader'},  # доступ на чтение кому угодно
    #     fields='id'
    # ).execute()
    #
    # imageList=[]
    # titleList = []
    # dateList = []
    # locationList = []
    # bedroomList = []
    # descriptionsList = []
    # priceList = []




    def pagination():
        WebDriverWait(browser, 60).until(
            EC.visibility_of_any_elements_located((By.CLASS_NAME, "pagination")))
        pagin = browser.find_element(By.CLASS_NAME, 'pagination').find_element(By.CLASS_NAME, 'selected').text
        pagin = int(pagin) - 1
        browser.get(f"https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{pagin}/c37l1700273")
        if pagin >= 1:
            settings()
        else:
            # service.spreadsheets().values().append(spreadsheetId=spreadsheet['spreadsheetId'],
            #                                        range='apart!A:Z',
            #                                        body={'majorDimension': "COLUMNS",
            #                                              "values": [[imageList], [titleList], [locationList],
            #                                                         [bedroomList], [descriptionsList], [priceList]]},
            #                                        valueInputOption="USER_ENTERED"
            #                                        ).execute()

            print('Complete')
            #print(spreadsheet['spreadsheetUrl'])
            browser.quit()

    def image():
        link_image = browser.find_elements(By.TAG_NAME, 'img')
        for link in link_image:
            find_url = link.get_attribute('data-src')
            if find_url is not None:
                # imageList.append(find_url)
                conn.execute(image_sql.insert().values(image=find_url))



    def titles():
        title = browser.find_elements(By.CSS_SELECTOR, 'div.title')
        for item in title:
            # titleList.append(item.text)
            conn.execute(title_sql.insert().values(title=item.text))

    def date():
        date_posted = browser.find_elements(By.CLASS_NAME, 'date-posted')
        for dates in date_posted:
            if dates.text.find('ago') != -1:
                date_now = datetime.date.today()
                # dateList.append(date_now)
                conn.execute(date_sql.insert().values(date=date_now.strftime('%d/%m/%Y')))
            else:
                # dateList.append(dates.text)
                conn.execute(date_sql.insert().values(date=dates.text))

    def locations():
        location = browser.find_elements(By.CLASS_NAME, 'location')
        for item in location:
            local = item.find_element(By.TAG_NAME, 'span').text
            # locationList.append(local)
            conn.execute(location_sql.insert().values(location=local))

    def bedroom():
        bedrooms = browser.find_elements(By.CLASS_NAME, 'bedrooms')
        for bed in bedrooms:
            # bedroomList.append(bed.text[5:])
            conn.execute(bedroom_sql.insert().values(bedroom=bed.text[5:]))

    def descriptions():
        description = browser.find_elements(By.CLASS_NAME, 'description')
        for desc in description:
            conn.execute(descriptions_sql.insert().values(descriptions=desc.text))
            # descriptionsList.append(desc.text)

    def prices():
        price = browser.find_elements(By.CLASS_NAME, 'price')
        for item in price:
            # priceList.append(item.text)
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
