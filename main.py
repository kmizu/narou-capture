import time
import json
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image, ImageDraw
from io import BytesIO
import os
import platform
import datetime

# ラベルとURLのペア
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

items = config['items']
interval = config['interval']
keywords = config['keywords']

# ChromeDriverを起動
options = Options()
options.add_argument('--window-size=800,600')
options.add_argument('--headless')
options.add_argument('log-level=3')
browser = webdriver.Chrome(options)

browser.execute_script("document.body.style.overflow = 'hidden';")

def save_screenshot(driver, file_path, keywords, is_full_size=False):
    # スクリーンショット設定
    screenshot_config = {
        "captureBeyondViewport": is_full_size,
    }

    # スクリーンショット取得
    base64_image = driver.execute_cdp_cmd("Page.captureScreenshot", screenshot_config)

    # Base64をデコードしてPILイメージに変換
    image = Image.open(BytesIO(base64.b64decode(base64_image['data'])))

    found = False
    for keyword in keywords:
        keyword_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]/../../../..")
        for keyword_element in keyword_elements:
            found = True
            # 要素の位置とサイズを取得
            location = keyword_element.location
            size = keyword_element.size

            # 作品枠全体に太い赤線の枠を描画
            draw = ImageDraw.Draw(image)
            left = location['x']
            top = location['y']
            right = location['x'] + size['width']
            bottom = location['y'] + size['height']
            draw.rectangle((left, top, right, bottom), outline='red', width=5)

    if found:
        # ファイル書き出し
        image.save(file_path)
    return found

def capture(label, url):
    now = datetime.datetime.now()
    now_string = now.strftime('%Y-%m-%d-%H%M')
    browser.get(url)
    browser.refresh()

    # OSを判別して出力ディレクトリを設定
    if platform.system() == 'Windows':
        home_path = os.environ['HOMEPATH']
        out_dir = f"{home_path}/Dropbox/gacha_contest/{label}"
    else:  # Linux の場合
        home_path = os.environ['HOME']
        out_dir = f"{home_path}/Dropbox/gacha_contest/linux/{label}"
    os.makedirs(out_dir, exist_ok=True)

    found = save_screenshot(
        browser, 
        f"{out_dir}/スクリーンショット_{now_string}.png",
        keywords,
        is_full_size=True
    )
    if found:
        print(f"スクリーンショット {label} ({now_string}) をキャプチャしました")

while True:
    print("キャプチャ開始：")
    for label, url in items.items():
        capture(label + "_01_050", url + "?p=1")
        capture(label + "_51_100", url + "?p=2")
    print("キャプチャ終了：")
    
    # 指定した間隔だけ待機
    time.sleep(interval)
