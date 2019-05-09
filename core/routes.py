import os

from .views import index, filmDetals

__all__ = ('setup_routes',)


def setup_routes(app):
    app.router.add_static('/static/',
                          path=os.path.abspath('./static/'),
                          name='static')
    app.router.add_get('/', index)
    app.router.add_get('/{filmID}', filmDetals)