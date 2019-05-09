import aiohttp
import argparse
import asyncio
import logging
import os

from core.main import create_app
from core.settings import load_config


formatter = logging.Formatter('%(asctime)s | %(name)s | %(module)s | line:%(lineno)d | %(levelname)-8s: %(message)s')
log_path = os.path.abspath('logs')
if not os.path.exists(log_path):
    os.mkdir(log_path)
log_file = 'logs/main.log'
logger = logging.getLogger('main')
logger.setLevel(logging.WARNING)
fh = logging.FileHandler(log_file, 'w')
fh.setFormatter(formatter)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

parser = argparse.ArgumentParser(description="Moves Releases")
parser.add_argument('--debug', action="store_true", help="Debug")
parser.add_argument("-c", "--config", type=argparse.FileType('r'),
                    help="Path to configuration file")
args = parser.parse_args()

configure = load_config(args.config)

if args.debug:
    logger.setLevel(logging.DEBUG)

app = create_app(config=configure)


if __name__ == '__main__':
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        logging.exception('Library uvloop is not available')

    try:
        aiohttp.web.run_app(app, host=configure['host'], port=configure['port'])
    except Exception as err:
        logging.exception(err)
    finally:
        pass
