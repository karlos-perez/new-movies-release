from aiohttp_socks import SocksConnector, SocksVer, SocksError

import aiohttp
import jinja2
import aiohttp_jinja2

from .routes import setup_routes
from .middlewares import setup_middlewares


def get_connector(**proxy):
    connector = SocksConnector(socks_ver=SocksVer.SOCKS5,
                               host=proxy['ip'],
                               port=proxy['port'],
                               username=proxy['user'],
                               password=proxy['password'],
                               rdns=True)
    return connector


async def create_app(config: dict):
    app = aiohttp.web.Application()
    app['config'] = config
    aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('core', 'templates'))
    setup_routes(app)
    setup_middlewares(app)
    app.on_startup.append(on_start)
    app.on_cleanup.append(on_shutdown)
    return app


async def on_start(app):
    if app['config'].get('proxy'):
        connector = get_connector(**app['config']['proxy'])
    else:
        connector = None
    session = aiohttp.ClientSession(connector=connector)
    app['session'] = session


async def on_shutdown(app):
    await app['session'].close()
