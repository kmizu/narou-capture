import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
import os
import platform
import datetime

# ラベルとURLのペア
items = {
    '日間_総合_すべて':           "https://yomou.syosetu.com/rank/list/type/daily_total/",       
    '日間_総合_短編':             "https://yomou.syosetu.com/rank/list/type/daily_t/",          
    '日間_総合_完結済':           "https://yomou.syosetu.com/rank/list/type/daily_er/",
    '日間_総合_連載中':           "https://yomou.syosetu.com/rank/list/type/daily_r/",
    '日間_異世界恋愛_すべて':     "https://yomou.syosetu.com/rank/genrelist/type/daily_101/",
    '日間_異世界恋愛_短編':       "https://yomou.syosetu.com/rank/genrelist/type/daily_101_t/",
    '日間_異世界恋愛_完結済':     "https://yomou.syosetu.com/rank/genrelist/type/daily_101_er/",
    '日間_異世界恋愛_連載中':     "https://yomou.syosetu.com/rank/genrelist/type/daily_101_r/",
}

# ChromeDriverを起動
options = Options()
options.add_argument('--headless')
options.add_argument('log-level=3')
browser = webdriver.Chrome(options)

# スクリーンショットを撮る間隔（秒）
interval = 60 * 30 # 30分

count = 1

def capture(label, url):
    now = datetime.datetime.now()
    now_string = now.strftime('%Y-%m-%d-%H%M')
    browser.get(url)

    # ページの高さを取得
    page_height = browser.execute_script("return document.body.scrollHeight")
    
    # ウィンドウの高さを取得
    window_height = browser.execute_script("return window.innerHeight")
    
    # スクロール操作を行いながらスクリーンショットを撮る
    screenshots = []
    for offset in range(0, page_height, window_height):
        browser.execute_script(f"window.scrollTo(0, {offset});")
        time.sleep(1)  # スクロール後の読み込み待ち
        screenshots.append(browser.get_screenshot_as_png())
    
    # スクリーンショットを結合してページ全体のスクリーンショットを作成
    full_screenshot = Image.new('RGB', (browser.get_window_size()['width'], page_height))
    offset = 0
    for screenshot in screenshots:
        image = Image.open(BytesIO(screenshot))
        full_screenshot.paste(image, (0, offset))
        offset += image.size[1]
    
    # OSを判別して出力ディレクトリを設定
    if platform.system() == 'Windows':
        home_path = os.environ['HOMEPATH']
        out_dir = f"{home_path}/Dropbox/gacha_contest/{label}"
    else:  # Linux の場合
        home_path = os.environ['HOME']
        out_dir = f"{home_path}/Dropbox/gacha_contest/linux/{label}"
    os.makedirs(out_dir, exist_ok=True)
    full_screenshot.save(f"{out_dir}/スクリーンショット_{now_string}.png")
    print(f"スクリーンショット {label} ({now_string}) をキャプチャしました")

while True:
    # ページを更新
    browser.refresh()
    print(f"ページをリフレッシュしました")

    print("キャプチャ開始：")
    for label, url in items.items():
        capture(label + "_01_050", url + "?p=1")
        capture(label + "_51_100", url + "?p=2")
    print("キャプチャ終了：")
    
    count += 1
    
    # 指定した間隔だけ待機
    time.sleep(interval)
