import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--name=narou_capture',
    '--onefile',
    '--noconsole',
    '--add-data=config.json:.',
    '--hidden-import=selenium.webdriver.chrome.options',
])
