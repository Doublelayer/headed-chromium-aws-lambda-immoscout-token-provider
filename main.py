import json
import os
import time
import undetected_chromedriver as uc
from pyvirtualdisplay import Display
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tempfile import mkdtemp


def get_uc_driver():
    options = uc.ChromeOptions()
    options.headless = False
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--single-process")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")

    driver_executable_path = '/tmp/chromedriver'
    os.system(f'cp /opt/chromedriver {driver_executable_path}')
    os.chmod(driver_executable_path, 0o777)

    driver = uc.Chrome(options=options,
                       browser_executable_path='/opt/chrome/chrome',
                       driver_executable_path=driver_executable_path,
                       version_main=114)  # , use_subprocess=True)

    return driver


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
                time.sleep(5)
                print("waiting for cookie...")
                WebDriverWait(driver, 10).until(lambda driver: "roboter" not in driver.title.lower())
                reese_token = WebDriverWait(driver, timeout=10).until(lambda d: d.get_cookie('reese84'))['value']
                print(f"reese84 cookie found: {reese_token}")
                new_token = f"reese84={reese_token};"
                print("SUCCESS! driver quiting...")

                return {
                    'statusCode': 200,
                    'body': new_token
                }

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
            'statusCode': 200,
            'body': json.dumps({'error': f'{e}'})
        }
