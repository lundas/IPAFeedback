import csv
import os
import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from datetime import datetime, date

class GoogleAPI:
    # argparse only relevant for command line - throws error in jupyter
    try:
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None

    # If modifying these scopes, delete your previous saved credentials at
    # ~/.credentials/sheets.googleapis.com-python-gAPItest.json
    scopes = 'https://www.googleapis.com/auth/spreadsheets'
    #uses Oauth ID rather than service account
    client_secret_file = '/PATH/TO/CREDENTIALS/'
    application_Name = 'Allocations'

    def get_credentials(self):
        """get valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid, 
        the Oauth2 flow is completed to obtain new credentials

        Returns:
            Credentials, the obtained credentials.
        """

        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 
            'sheets.googleapis.com-python-gAPItest.json')#change for each project for different credentials


        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.client_secret_file, self.scopes)
            flow.user_agent = self.application_Name
            if self.flags:
                credentials = tools.run_flow(flow, store, self.flags)
            else:
                tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def import_data(self, PATH):
        print("Interacting w/ Google Sheets API")
        # Populates Google Sheets. Dependent on Pandas
        credentials = GoogleAPI().get_credentials()
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?', 
            'version=v4')
        service = discovery.build('sheets', 'v4', http=http)
        spreadsheetID = '' #taken from url; change for each project

        # Read csv files to be imported
        trTransFile = open(PATH + 'trTransfers.csv')
        trTransReader = csv.reader(trTransFile)
        trTransData = list(trTransReader)

        # Populate Google Sheets with csv data
        # Taproom Transfers - sheet is named Taproom Transfers
        trTransBody = {u'range': u'Taproom Transfers!A1:H1500', 
                     u'values': trTransData, u'majorDimension': u'ROWS'}
        # clear sheet first to ensure no extra rows from last import
        result = service.spreadsheets().values().clear(spreadsheetId=spreadsheetID, 
                                                       range=trTransBody['range'], 
                                                       body={}).execute()
        # import csv data to Google Sheet - Taproom Transfers
        result = service.spreadsheets().values().update(spreadsheetId=spreadsheetID, 
                                                        range=trTransBody['range'],
                                                        valueInputOption='USER_ENTERED', 
                                                        body=trTransBody).execute()
        # # Insert last updated date
        today = [['Last Update:', str(datetime.today())]] #must be a list of lists
        updatedBody = {u'range': u'Taproom Transfers!I1:J1', u'values': today, 
                       u'majorDimension': u'ROWS'}
        # clear last updated cell
        result = service.spreadsheets().values().clear(spreadsheetId=spreadsheetID, 
                                                       range=updatedBody['range'],
                                                       body = {}).execute()
        # insert today's date
        result = service.spreadsheets().values().update(spreadsheetId=spreadsheetID, 
                                                        range=updatedBody['range'],
                                                        valueInputOption='USER_ENTERED', 
                                                        body=updatedBody).execute()
        return


