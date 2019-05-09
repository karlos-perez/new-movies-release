from aiohttp import web

import aiohttp_jinja2
import logging


__all__ = ('setup_middlewares',)

logs = logging.getLogger('main.middleware')


async def handle_404(request, response):
    result = aiohttp_jinja2.render_template('404.html',
                                            request,
                                            {'text': response})
    return result


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        if response.status == 200:
            return response
        logs.error(f'Response status: {response.status} - {response.message}')
        message = response.message
    except web.HTTPException as ex:
        logs.exception(f'HTTPException: {ex.status} - {ex.reason} - {request.url}')
        message = ex.reason
    error =  await handle_404(request, message)
    return error


def setup_middlewares(app):
    app.middlewares.append(error_middleware)