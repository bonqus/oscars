import csv
import re
from urllib.request import urlopen

from bs4 import BeautifulSoup


class ProfileScraper:
    BASE_URL = "https://www.imdb.com/"
    FIRST_PAGE_URL = "user/{}/ratings"

    @staticmethod
    def find_rankings(imdb_id):
        '''Scrapes imdb
        to find all the titles and their rankings for an imdb user
        :returns: imdb title ids and the users rating of them
        :rtype: dict
        '''
        movies = {}
        path = ProfileScraper.FIRST_PAGE_URL.format(imdb_id)
        while path is not None:
            context = urlopen(ProfileScraper.BASE_URL + path)
            html = context.read()
            context.close()
            page = BeautifulSoup(html, "html.parser")
            movies = {**movies, **ProfileScraper._find_ranked_movies(page)}
            path = ProfileScraper._find_next_page(page)
        return movies

    @staticmethod
    def _find_ranked_movies(page):
        '''Finds all the ranked movies on a page
        :param page: a bs page
        :returns: imdb titles ids and the users rating of them
        :rtype: dict
        '''
        movies = {}
        ranked_movies = page.findAll('div', {'class': 'lister-item-content'})
        for movie in ranked_movies:
            movie_id = movie.find('div', {
                'data-tconst': re.compile(r".*")
            }).attrs['data-tconst']
            movie_rating = int(
                movie.findAll(
                    'span', {'class': 'ipl-rating-star__rating'})[1].getText())
            movies[movie_id] = movie_rating
        return movies

    @staticmethod
    def _find_next_page(page):
        '''Find the next page path
        :param page: a soup page
        :returns: path or None
        :rtype: string or None
        '''
        footer = page.find('div', {'class': 'footer filmosearch'})
        if footer is None:
            return None
        next_page = footer.find('a', {'class': 'next-page'})
        if next_page is None:
            return None
        return next_page.attrs['href']


if __name__ == '__main__':
    import json
    with open('imdb_profiles.csv', 'r') as csvfile:
        DATA = csv.reader(csvfile)
        IMDB_PROFILES = dict((rows[0], rows[1]) for rows in DATA)

    IMDB_ID = IMDB_PROFILES['Bohn']
    MOVIE_RATINGS = ProfileScraper.find_rankings(IMDB_ID)
    print(json.dumps(MOVIE_RATINGS, indent=4))
