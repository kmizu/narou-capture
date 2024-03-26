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

def save_screenshot(driver, file_path, keywords):
    found = False
    for keyword in keywords:
        keyword_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]/../../../..")
        for i, keyword_element in enumerate(keyword_elements):
            found = True
            # 要素のスクリーンショットを取得
            element_screenshot = keyword_element.screenshot_as_png
            image = Image.open(BytesIO(element_screenshot))

            # 作品枠全体に太い赤線の枠を描画
            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 0, image.width, image.height), outline='red', width=5)

            # 要素のスクリーンショットを保存
            image.save(f"{file_path.split('.')[0]}_{i+1}.png")

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
        keywords
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
