import time
import hashlib
import datetime
import json
import logging
import bs4

__all__ = ('releases', 'get_film', 'rutorTorrents',)

logs = logging.getLogger('main.parse')

KINOPOISK_BASE_URL = "https://ma.kinopoisk.ru"
KINOPOISK_BASE_URL2 = "https://ma.kinopoisk.ru/ios/5.0.0/"
KINOPOISK_UUID = "6730382b7a236cd964264b49413ed00f"
KINOPOISK_CLIENTID = "56decdcf6d4ad1bcaa1b3856"
KINOPOISK_API_SALT = "IDATevHDS7"
KINOPOISK_API_RELEAESES = "/k/v1/films/releases/digital?digitalReleaseMonth={}&limit=1000&offset=0&uuid={}"
KINOPOISK_API_FILMDETAIL = "getKPFilmDetailView?still_limit=9&filmID={}&uuid={}"
KINOPOISK_POSTER_URL = "https://st.kp.yandex.net/images/{}{}width=360"
RUTOR_BASE_URL = "http://rutor.info/search/0/0/010/0/film%20"


async def _fetch(session, url, headers=None, proxy=None):
    if proxy:
        pass
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            result = await response.text()
        else:
            logs.exception(f'Response status: {response.status} URL: {url}')
            result = None
        return result


async def get_release(app, month):
    logging.info('PARES')
    requestMethod = KINOPOISK_API_RELEAESES.format(month, KINOPOISK_UUID)
    timestamp = str(int(round(time.time() * 1000)))
    hashString = requestMethod + timestamp + KINOPOISK_API_SALT
    headers = {"Accept-encoding": "gzip",
               "Accept": "application/json",
               "User-Agent": "Android client (6.0.1 / api23), ru.kinopoisk/4.6.5 (86)",
               "Image-Scale": "3",
               "device": "android",
               "ClientId": KINOPOISK_CLIENTID,
               "countryID": "2",
               "cityID": "1",
               "Android-Api-Version": "23",
               "clientDate": datetime.date.today().strftime("%H:%M %d.%m.%Y"),
               "X-TIMESTAMP": timestamp,
               "X-SIGNATURE": hashlib.md5(
                   hashString.encode('utf-8')).hexdigest()}
    url = KINOPOISK_BASE_URL + requestMethod
    response = await _fetch(app['session'], url, headers)
    if not response:
        logs.error(f'Response is None: {response}')
        return None
    releases = json.loads(response)
    if releases.get('success') != True:
        logs.error(f'Response success is False: {response}')
        return None
    if not releases.get('data'):
        logs.error(f'Response data is False: {response}')
        return None
    data = releases.get('data')
    if not data.get('items'):
        logs.error(f'Response items is False: {response}')
        return None
    items = data.get('items')
    result = []
    for i in items:
        item = {}
        item['id'] = i['id']
        item['title'] = i['title']
        item['poster'] = i['poster']['url']
        item['year'] = i['year']
        item['duration'] = i['duration']
        item['releaseDate'] = i['contextData']['releaseDate']
        countries = []
        for c in i['countries']:
            countries.append(c['name'])
        item['countries'] = ', '.join(countries)
        genres = []
        for g in i['genres']:
            genres.append(g['name'])
        item['genres'] = ', '.join(genres)
        result.append(item)
    return result


async def releases(app, days=31):
    result = []
    currentDate = datetime.date.today() - datetime.timedelta(days=1)
    downloadDates = [currentDate]
    beginDate = datetime.date.today() - datetime.timedelta(days=days)
    iterationDate = datetime.date.today() - datetime.timedelta(days=1)
    while (beginDate.year != iterationDate.year) or (
           beginDate.month != iterationDate.month):
        iterationDate = iterationDate.replace(day=1) - datetime.timedelta(days=1)
        downloadDates.append(iterationDate)
    for downloadDate in downloadDates:
        response = await get_release(app, downloadDate.strftime("%m.%Y"))
        if response:
            for i in response:
                releaseDate = datetime.date.fromisoformat(i['releaseDate'])
                if beginDate <= releaseDate <= currentDate:
                    result.append(i)
        else:
            return None
    return result


async def get_film(app, filmID):
    requestMethod = KINOPOISK_API_FILMDETAIL.format(filmID, KINOPOISK_UUID)
    timestamp = str(int(round(time.time() * 1000)))
    hashString = requestMethod + timestamp + KINOPOISK_API_SALT
    headers = {"Accept-encoding": "gzip",
               "Accept": "application/json",
               "User-Agent": "Android client (6.0.1 / api23), ru.kinopoisk/4.6.5 (86)",
               "Image-Scale": "3",
               "device": "android",
               "ClientId": KINOPOISK_CLIENTID,
               "countryID": "2",
               "cityID": "1",
               "Android-Api-Version": "23",
               "clientDate": datetime.date.today().strftime("%H:%M %d.%m.%Y"),
               "X-TIMESTAMP": timestamp,
               "X-SIGNATURE": hashlib.md5(
                   hashString.encode('utf-8')).hexdigest()}
    url = KINOPOISK_BASE_URL2 + requestMethod
    response = await _fetch(app['session'], url, headers)
    if not response:
        return None
    detail = json.loads(response)['data']
    result = {}
    if detail.get('gallery'):
        stills = []
        for i in detail.get('gallery'):
            still = 'https://st.kp.yandex.net/images/' + i.get('preview')
            stills.append(still)
        result.update({'stills': stills})
    if detail.get('country'):
        result.update({'country': detail.get('country')})
    if detail.get('posterURL'):
        posterURL = detail.get('posterURL')
        if "?" in posterURL:
            posterURL = KINOPOISK_POSTER_URL.format(posterURL, "&")
        else:
            posterURL = KINOPOISK_POSTER_URL.format(posterURL, "?")
        result.update({'poster': posterURL})
    if detail.get('description'):
        result.update({'description': detail.get('description')})
    if detail.get('genre'):
        result.update({'genre': detail.get('genre')})
    if detail.get('nameRU'):
        result.update({'title': detail.get('nameRU')})
    if detail.get('webURL'):
        result.update({'link': detail.get('webURL')})
    if detail.get('filmLength'):
        result.update({'length': detail.get('filmLength')})
    if detail.get('year'):
        result.update({'year': detail.get('year')})
    if detail.get('rentData') and detail['rentData'].get('premiereDigital'):
        result.update({'releaseDate': detail['rentData']['premiereDigital']})
    return result


async def rutorTorrents(app, idFilm):
    headers = {"Accept-encoding": "gzip",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0)\
                              Gecko/20100101 Firefox/65.0"}
    url = RUTOR_BASE_URL + idFilm
    response = await _fetch(app['session'], url, headers)
    result = []
    body = bs4.BeautifulSoup(response, "html.parser")
    table = body.find('div', attrs={'id': 'index'}).find('table')
    tr = table.find_all('tr')
    for i in range(1, len(tr)):
        raw = {}
        td = tr[i].find_all('td')
        raw['dateCreate'] = td[0].getText().strip()
        a = td[1].find_all('a')
        raw['magnetLink'] = a[1].get('href')
        raw['name'] = a[2].getText().strip()
        raw['size'] = td[-2].getText().strip()
        span = td[-1].find_all('span')
        raw['distibute'] = span[0].getText().strip()
        raw['download'] = span[1].getText().strip()
        result.append(raw)
    return result