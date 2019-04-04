from src import GoogleAPI

# Initialize GoogleAPI class
gAPI = GoogleAPI.GoogleAPI()

# Define variables
PATH = '/PATH/TO/FILES'

# Import data to Google Sheets via API
gAPI.import_data(PATH)