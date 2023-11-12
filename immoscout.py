import json
import time
import boto3

from pyvirtualdisplay import Display
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from driver import get_uc_driver


def handler(event=None, context=None):
    print(event)
    print('--------------\n')

    try:
        display = Display(visible=0, size=(1024, 768))
        display.start()
        time.sleep(5)
        driver = get_uc_driver()

        attempt = 0
        while attempt <= 5:
            attempt += 1
            print("loading page ...")
            driver.get('https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-mieten')
            print("page loaded...")
            try:
                print("waiting for captcha box...")
                WebDriverWait(driver, 20) \
                    .until(EC.visibility_of_element_located((By.ID, "captcha-box"))) \
                    .click()
                print("captcha box was clicked...")
                print("waiting for cookie...")
                WebDriverWait(driver, 10).until(lambda driver: "roboter" not in driver.title.lower())
                reese_token = WebDriverWait(driver, timeout=10).until(lambda d: d.get_cookie('reese84'))['value']
                print(f"reese84 cookie found: {reese_token}")

                cookie_string = ""
                all_cookies = driver.get_cookies()
                for cookie in all_cookies:
                    cookie_string += f"{cookie['name']}={cookie['value']};"

                file_content = {
                    "cookieString": cookie_string,
                    "raw": driver.get_cookies()
                }

                s3 = boto3.client('s3')
                s3.put_object(Body=bytes(json.dumps(file_content).encode('UTF-8')), Bucket="immocookies", Key='immoscout-cookies.json')

                return file_content

            except TimeoutException:
                if "roboter" in driver.title.lower():
                    print("cannot find captcha box...")
                    continue

        return {
            'statusCode': 200,
            'body': None
        }
    except Exception as e:
        print(f'error in function: {e}')
        print('type is:', e.__class__.__name__)

        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'{e}'})
        }
