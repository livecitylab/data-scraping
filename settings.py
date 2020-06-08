# from shutil import which
#
# SELENIUM_DRIVER_NAME = 'firefox'
# SELENIUM_DRIVER_EXECUTABLE_PATH = which('geckodriver')
# SELENIUM_DRIVER_ARGUMENTS=['-headless']

ROTATING_PROXY_LIST_PATH = 'proxies/proxies.txt'


DOWNLOADER_MIDDLEWARES = {
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    # 'scrapy_selenium.SeleniumMiddleware': 800
}
