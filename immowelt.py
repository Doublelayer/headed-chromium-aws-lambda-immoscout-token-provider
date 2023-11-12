import json
import time
from pyvirtualdisplay import Display

from driver import get_uc_driver


def handler(event=None, context=None):
    print(event)
    print('--------------\n')

    try:
        display = Display(visible=0, size=(1024, 768))
        display.start()
        time.sleep(5)
        driver = get_uc_driver()

        print("loading page ...")
        driver.get('https://www.immowelt.de/suche/berlin/wohnungen/mieten')
        print("page loaded...")
        bearer_token = driver.execute_script(
            'return window.localStorage.getItem("residential.search.ui.oauth.access.token");')

        cookie_string = ""
        all_cookies = driver.get_cookies()
        for cookie in all_cookies:
            cookie_string += f"{cookie['name']}={cookie['value']};"

        return {
            "cookieString": cookie_string,
            "cookies_raw": driver.get_cookies(),
            "bearer_token": bearer_token
        }

    except Exception as e:
        print(f'error in function: {e}')
        print('type is:', e.__class__.__name__)

        return {
            'statusCode': 200,
            'body': json.dumps({'error': f'{e}'})
        }
