ROTATING_PROXY_LIST_PATH = './proxies/proxies.txt'

# This setting is also affected by the RANDOMIZE_DOWNLOAD_DELAY setting (which is enabled by default).
# By default, Scrapy doesn’t wait a fixed amount of time between requests,
# but uses a random interval between 0.5 * DOWNLOAD_DELAY and 1.5 * DOWNLOAD_DELAY.
DOWNLOAD_DELAY = 2

DOWNLOADER_MIDDLEWARES = {
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
}
