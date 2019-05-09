from aiohttp_jinja2 import template
from aiohttp import web

import logging

from .parse import rutorTorrents, get_film, releases


DAYS = 31

logs = logging.getLogger('main.view')


@template('index.html')
async def index(request):
    site_name = request.app['config'].get('site_name')
    movies = await releases(request.app, days=DAYS)
    if movies:
        return {'site_name': site_name,
                'releases': movies,
                'amount': len(movies),
                'days': DAYS}
    else:
        raise web.HTTPNotFound(text=f'Result is None')


@template('detail.html')
async def filmDetals(request):
    idFilm = request.match_info.get('filmID')
    if idFilm and idFilm.isdigit():
        result = await get_film(request.app, int(idFilm))
    else:
        logs.error(f'filmID is not integer: {type(idFilm)} - {idFilm}')
        raise web.HTTPNotFound(text=f'filmID is not integer')
    if result:
        torrents = await rutorTorrents(request.app, idFilm)
        result['torrents'] = torrents
    else:
        raise web.HTTPNotFound(text=f'Result is None')
    return result


