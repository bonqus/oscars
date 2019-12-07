import rarbgapi
import requests
import yaml
from tqdm import tqdm

from google_sheets_api import GoogleSheetsApi
from imdb_profile_scraper import find_rankings

with open('configuration.yaml', 'r') as yaml_file:
    CFG = yaml.load(yaml_file, Loader=yaml.FullLoader)

# If modifying SCOPES, delete the file token.pickle
SCOPES = CFG['scopes']
# The ID of the spreadsheet
SPREADSHEET_ID = CFG['spreadsheet_id']

GSA = GoogleSheetsApi(SCOPES, SPREADSHEET_ID)

print('Getting movie ids')
MOVIE_IDS = [movie_id for [movie_id] in GSA.read('Movies!A2:A')]
print('Getting user ids')
USER_IDS = [user_id for [user_id] in GSA.read('Users!B2:B')]

OMDB_URL = 'http://www.omdbapi.com/'
YTS_URL = 'https://yts.lt/api/v2/list_movies.json'
RARBG_URL = 'https://unblockedrarbg.org/torrents.php?imdb={}&category%5B%5D=14&category%5B%5D=48&category%5B%5D=17&category%5B%5D=44&category%5B%5D=45&category%5B%5D=47&category%5B%5D=50&category%5B%5D=51&category%5B%5D=52&category%5B%5D=42&category%5B%5D=46'

USERS_RATINGS = []
print('Scraping user ratings')
for user_id in tqdm(USER_IDS):
    USERS_RATINGS.append(find_rankings(user_id))

DATA = []
print('Creating data rows')
for movie_id in tqdm(MOVIE_IDS):
    OMDB_PARAMS = {
        'apikey': CFG['omdb_api_key'],
        'i': movie_id,
    }
    YTS_PARAMS = {'query_term': movie_id}

    omdb_response = requests.get(OMDB_URL, params=OMDB_PARAMS)
    omdb_result = omdb_response.json()

    yts_response = requests.get(YTS_URL, params=YTS_PARAMS)
    yts_result = yts_response.json()
    yts_data = ''
    if yts_result['data']['movie_count'] > 0:
        try:
            yts_data = '=HYPERLINK("{}","YTS")'.format(
                yts_result['data']['movies'][0]['url'])
        except KeyError:
            print(movie_id)
            print(yts_result['data'])

    rarbg = rarbgapi.RarbgAPI()
    rarbg_result = rarbg.search(search_imdb=movie_id)

    rarbg_data = ''
    if len(rarbg_result) > 0 or rarbg_result:
        rarbg_data = '=HYPERLINK("{}","RARBG")'.format(
            RARBG_URL.format(movie_id))

    DATA_USERS_RATINGS = []
    for user_rating in USERS_RATINGS:
        if movie_id in user_rating:
            DATA_USERS_RATINGS.append(user_rating[movie_id])
        else:
            DATA_USERS_RATINGS.append('')

    DATA.append([
        '=HYPERLINK("https://www.imdb.com/title/{}","{}")'.format(
            movie_id, omdb_result['Title']),
        omdb_result['Released'],
        yts_data,
        rarbg_data,
        omdb_result['Runtime'],
        omdb_result['Genre'],
        omdb_result['Director'],
        omdb_result['Writer'],
        omdb_result['Plot'],
        omdb_result['Language'],
        omdb_result['Country'],
        omdb_result['Metascore'],
        omdb_result['imdbRating'],
    ] + DATA_USERS_RATINGS)

# GSA.append('Movies!B2:B', 'USER_ENTERED', DATA)
GSA.write('Movies!B2:AA', 'USER_ENTERED', DATA)
