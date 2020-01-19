# The Oscars
A profile scraper and google sheets updater

## Installation
`$ git clone https://github.com/mbonus/oscars.git`

`$ cd oscars/`

#### Virtual environment 
`$ python3 -m venv virt_env`

`$ source virt_env/bin/activate`

##### Requirements (the requirements are bloated because of linting and such)
`$ pip install -r requirements.txt`

##### Create a configuration.yaml file
```
$ echo 
"spreadsheet_id: '<spreadsheet_id>'
scopes:
  - 'https://www.googleapis.com/auth/spreadsheets'
omdb_api_key: '<omdb_api_key>'" >> configuration.yaml`
```

##### Run it
`$ python imdb_id_finder.py`
fix missing imdb ids and fix urls manual, imdb_id_finder should be run once against predictions, shortlits or nominations
`$ python main.py`
run main everytime you want to update ratings and movie info
