import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GoogleSheetsApi():
    ''' Google sheets api helper class
    :param scopes: read / write privligies
    '''
    def __init__(self, scopes, spreadsheet_id):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', scopes)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)
        self.sheet = self.service.spreadsheets()
        self.spreadsheet_id = spreadsheet_id

    def read(self, range_name):
        """Read data from the initialized sheet

        :param range_name: A1 nottion range to reed, 'Movies!A2:E2'
        :returns: A list of lists with the read values
        :rtype: list<list<string>>

        """
        result = self.sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
        ).execute()
        return result.get('values', [])

    def append(self, range_name, value_input_option, values):
        """Appending googlesheets values

        :param range_name: sheet and range
        :param value_input_option: RAW or USER_ENTERED
        :param values: the values to append

        """
        body = {'values': values}
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body).execute()


if __name__ == '__main__':
    import yaml
    with open('configuration.yaml', 'r') as yaml_file:
        CFG = yaml.load(yaml_file, Loader=yaml.FullLoader)

    # If modifying SCOPES, delete the file token.pickle
    SCOPES = CFG['scopes']
    # The ID of the spreadsheet
    SPREADSHEET_ID = CFG['spreadsheet_id']
    GSA = GoogleSheetsApi(SCOPES, SPREADSHEET_ID)
    print(GSA.read('Movies'))
    GSA.append('Movies', 'RAW', [[4, 1, 1, 4]])
