import re
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup
from lxml import html

BASE_URL = "https://www.imdb.com/"
FIRST_PAGE_URL = "user/{}/ratings"

# python ratings.py  172,12s user 1,00s system 51% cpu 5:35,44 total


def find_rankings(imdb_id, number_of_pages=1):
    '''Scrapes imdb
    to find all the titles and their rankings for an imdb user
    :param imdb_id: the imdb user id
    :param number_of_pages: The number of pages to scrape, 0 for all pages.
    :returns: imdb title ids and the users rating of them
    :rtype: dict
    '''
    movies = {}
    path = FIRST_PAGE_URL.format(imdb_id)
    page_counter = 1
    while path is not None:
        page = requests.get(BASE_URL + path)
        tree = html.fromstring(page.content)
        movies = {**movies, **_find_ranked_movies(tree)}
        path = _find_next_page(tree)
        if number_of_pages == page_counter:
            break
        page_counter += 1
    return movies


def _find_ranked_movies(tree):
    '''Finds all the ranked movies on a page
    :param page: a bs page
    :returns: imdb titles ids and the users rating of them
    :rtype: dict
    '''
    ids = tree.xpath(
        '//div[@class="lister-item mode-detail"]/div[@class="lister-item-image ribbonize"]/@data-tconst'
    )
    ratings = tree.xpath(
        "//div[@class='lister-item mode-detail']/div[@class='lister-item-content']/div[@class='ipl-rating-widget']/div[@class='ipl-rating-star ipl-rating-star--other-user small']/span[@class='ipl-rating-star__rating']/text()"
    )
    return dict(zip(ids, ratings))
    # ranked_movies = page.findAll('div', {'class': 'lister-item-content'})
    # for movie in ranked_movies:
    #     movie_id = movie.find('div', {
    #         'data-tconst': re.compile(r".*")
    #     }).attrs['data-tconst']
    #     movie_rating = int(
    #         movie.findAll('span',
    #                       {'class': 'ipl-rating-star__rating'})[1].getText())
    #     movies[movie_id] = movie_rating
    # return movies


def _find_next_page(tree):
    '''Find the next page path
    :param page: a soup page
    :returns: path or None
    :rtype: string or None
    '''
    # footer = page.find('div', {'class': 'footer filmosearch'})
    # if footer is None:
    #     return None
    # next_page = footer.find('a', {'class': 'next-page'})
    # if next_page is None:
    #     return None
    # return next_page.attrs['href']
    next_page = tree.xpath(
        "//div[@class='footer filmosearch']/div[@class='desc']/div[@class='list-pagination']/a[@class='flat-button lister-page-next next-page']/@href"
    )
    if len(next_page) > 0:
        return next_page[0]
    else:
        return None


if __name__ == '__main__':
    import json
    import csv
    with open('imdb_profiles.csv', 'r') as csvfile:
        DATA = csv.reader(csvfile)
        IMDB_PROFILES = dict((rows[0], rows[1]) for rows in DATA)

    IMDB_ID = IMDB_PROFILES['Bohn']
    MOVIE_RATINGS = find_rankings(IMDB_ID)
    print(json.dumps(MOVIE_RATINGS, indent=4))
