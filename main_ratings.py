import yaml

from google_sheets_api import GoogleSheetsApi
from imdb_profile_scraper import find_rankings
from tqdm import tqdm

# parser = argparse.ArgumentParser()
# parser.add_argument('-n',
#                     type=int,
#                     default=0,
#                     help='Number of user imdb pages to scan')
# args = parser.parse_args()
# pages = args.n
pages = 0

with open('configuration.yaml', 'r') as yaml_file:
    CFG = yaml.load(yaml_file, Loader=yaml.FullLoader)

# If modifying SCOPES, delete the file token.pickle
SCOPES = CFG['scopes']
# The ID of the spreadsheet
SPREADSHEET_ID = CFG['spreadsheet_id']

GSA = GoogleSheetsApi(SCOPES, SPREADSHEET_ID)

print('Getting movie ids')
MOVIE_IDS = [movie_id for [movie_id] in GSA.read('Overview!A2:A')]

print('Getting user ids')
USER_IDS = [user_id for [user_id] in GSA.read('Users!B2:B')]


USERS_RATINGS = []
print('Scraping user ratings')
for user_id in tqdm(USER_IDS):
    USERS_RATINGS.append(find_rankings(user_id, pages))

DATA = []
print('Creating data rows')
for movie_id in tqdm(MOVIE_IDS):
    OMDB_PARAMS = {
        'apikey': CFG['omdb_api_key'],
        'i': movie_id,
    }

    DATA_USERS_RATINGS = []
    for user_rating in USERS_RATINGS:
        if movie_id in user_rating:
            DATA_USERS_RATINGS.append(user_rating[movie_id])
        else:
            DATA_USERS_RATINGS.append('')
    DATA.append(DATA_USERS_RATINGS)

# GSA.append('Movies!B2:B', 'USER_ENTERED', DATA)
GSA = GoogleSheetsApi(SCOPES, SPREADSHEET_ID)
GSA.write('Overview!R2:AZ', 'USER_ENTERED', DATA)
