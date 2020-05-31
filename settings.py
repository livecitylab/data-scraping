ROTATING_PROXY_LIST_PATH = 'proxies/proxies.txt'

DOWNLOADER_MIDDLEWARES = {
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
}
