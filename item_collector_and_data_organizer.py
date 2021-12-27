import time
import os
import argparse
import json
import logging
import posixpath
import requests

import wikipediaapi
from collections import OrderedDict
from geopy.geocoders import Nominatim


class WikipediaInfo(object):

    """
    Helper class to fetch information from wikipedia pages using Python APIs
    API Documentation:
        https://wikipedia-api.readthedocs.io/en/latest/README.html
    """

    def __init__(self, pageName, lang):
        """
        Initialize Wikipedia Page object and fetch information from wikipedia
        Args:
            pageName(str): Wikipedia page name
            lang(str): shorthand character for language in which information 
                       need to be fetched e.g. for English = 'en'
        """
        self.wikiObj = wikipediaapi.Wikipedia(lang)
        self.wikiPage = self.wikiObj.page(pageName)
        if not self.wikiPage.exists():
            logging.error("Wikipedia page for '{}' does not exists!".format(
                pageName))
        else:
            logging.info("Wikipedia page for '{}' successfully loaded!".format(
                pageName))
    
    @property
    def summary(self): 
        """
        Text from summary section of Wikipedia page of city
        """
        logging.info("Fetched summary from wikipedia")
        return self.wikiPage.summary
    
    
    @property
    def url(self):
        """
        Wikipedia page url
        """
        logging.info("Fetched wikipedia url of the city")
        return self.wikiPage.fullurl
    
    @property
    def sections(self):
        """
        Wikipedia sections of pages
        # TODO: Check if this can be used further
        """
        return self.wikiPage.sections

 
class GeoLocator(object):

    """
    Helper class to fetch Geolocation of the places using Python APIs
    API Documentation:
        https://geopy.readthedocs.io/en/stable/
    """    
    
    USER_AGENT = "aditya" # TODO: Replace this with project name

    def __init__(self, place):
        """
        Fetch location info using geocoder REST APIs
        Args:
            place(str): Name of the place whose geolocation need to be fetched 
        """
        self.geolocator = Nominatim(user_agent=self.USER_AGENT)
        self.location = self.geolocator.geocode(place)
    
    @property
    def address(self): 
        """
        Short address of the place
        """
        logging.info("Fetching address success!")
        return self.location.address
    
    @property
    def latitude(self):
        """
        Langitude of the place
        """
        logging.info("Fetching latitude success!")
        return self.location.latitude

    @property
    def longitude(self):
        """
        Logitude of the place
        """
        logging.info("Fetching longitude success!")
        return self.location.longitude


class OpenTripMapHelper(object):
    
    """
    Helper class to fetch information about nearby places using REST APIs
    API Documentation:
        https://opentripmap.io/docs
    """
    
    # TODO: Encrypt this key and store
    KEY = "5ae2e3f221c38a28845f05b62c0d88ebaa249904339a4644791d1dcb"
    SERVER_URL = "https://api.opentripmap.com/0.1/"
    # TODO: Check if any additional API end point need to be used 
    #       Accordingly update the structure of the code here
    API_ENDPOINT = "places" 
    
    def __init__(self, city, lang):
        self.city = city
        self.lang = lang
 
    @classmethod
    def getUrl(cls, lang, method, query=""):
        """
        Builds and returns the url for REST call
        lang(str): shorthand character for language in which information 
                   need to be fetched e.g. for English = 'en'
        method(str): Sub-method of API endpoint with which info 
                     need to be fetch
        query(str)(optional): Additonal configurations for REST query
        """
        url = posixpath.join(cls.SERVER_URL, lang, cls.API_ENDPOINT, method)
        url = "{url}?apikey={key}".format(url=url, key=cls.KEY)
        if query:
            url = "{url}&{query}".format(url=url, query=query)
        return url
    
    @staticmethod
    def runQuery(url):
        """
        Run GET query and return response
        As of now don't see any other use case except GET method
        # TODO: Check the truthness of above statement and refactor accordingly
        """
        response = requests.get(url)
        if response.status_code != 200:
            logging.error("GET with {} failed!".format(url))
            response = None
        else:
            logging.info("GET with {} success!".format(url))
        return response
    
    @property
    def timezone(self):
        """
        Get Population of the city
        """
        url = self.getUrl(lang=self.lang, method='geoname',
                 query="name={}".format(self.city))
        response = self.runQuery(url)
        if response:
            logging.info("Timezone fetched succesfully!")
            return response.json()["timezone"]         
        logging.error("Failed to fetch timezone!")

    @property
    def population(self):
        """
        Get Population of the city
        """
        url = self.getUrl(lang=self.lang, method='geoname',
                 query="name={}".format(self.city))
        response = self.runQuery(url)
        if response:
            logging.info("population fetched successfully!")
            return response.json()["population"]
        logging.error("failed to fetch population!")         
    
    @property
    def latitude(self):
        """
        Get latitude of the city
        """
        url = self.getUrl(lang=self.lang, method='geoname',
                 query="name={}".format(self.city))
        response = self.runQuery(url)
        if response:
            logging.info("latitude fetched successfully!")
            return response.json()["lat"]
        logging.error("failed to fetch latitude!")         
         
    @property
    def longitude(self):
        """
        Get latitude of the city
        """
        url = self.getUrl(lang=self.lang, method='geoname',
                 query="name={}".format(self.city))
        response = self.runQuery(url)
        if response:
            logging.info("longitude fetched successfully!")
            return response.json()["lon"]
        logging.error("failed to fetch longitude!")         
    
    @property
    def interestingPlaces(self):
        """
        Get Interesting places of the city
        """
        url = self.getUrl(lang=self.lang, method='radius',
                query="radius=1000&limit={}&offset={}&lon={}"
                      "&lat={}&rate=3&format=json".format(
                        10, 0, self.longitude, self.latitude))
        response = self.runQuery(url)
        if response:
            logging.info("interesting places fetched successfully!")
            return [item["name"] for item in response.json()]
        logging.error("failed to fetch interesting places!")         


wikiInfoObj = None
geoObj = None
otMapObj = None
wikiUrl = None

def setupInfoFetchObjects(cityName, language):
    
    global wikiInfoObj
    global geoObj
    global otMapObj
    
    logging.info("")
    logging.info("")    
    logging.info("*" * 80)
    logging.info("Start: Item Collection")
    logging.info("Selected City: {}".format(cityName))
    logging.info("Selected Language: {}".format(language))
    logging.info("*" * 80)
    
    logging.info("")
    logging.info("***** Setting up GeoLocation information fetch")
    geoObj = GeoLocator(cityName)
    
    logging.info("")
    logging.info("****** Setting up information fetch"
                 " about interesting nearby places")
    otMapObj = OpenTripMapHelper(cityName, language)

    logging.info("")
    logging.info("***** Setting up information fetch from Wikipedia")
    logging.info("")
    wikiInfoObj = WikipediaInfo(cityName, language)    

 
def populateAttributeMap(city, language):

    global wikiInfoObj
    global geoObj
    global otMapObj
    global wikiUrl

    wikiUrl = wikiInfoObj.url,
    
    attributeMap = OrderedDict({
        # "address": geoObj.address,
        "Wikipedia Summary": wikiInfoObj.summary,
        "Latitude": geoObj.latitude,
        "Longitude": geoObj.longitude,
        "Population": otMapObj.population,
        "Timezone": otMapObj.timezone,
        "Interesting Places": otMapObj.interestingPlaces
    })
    return attributeMap


def prettyPrint(dictData):
    logging.debug(json.dumps(dictData, indent=4))

 
def fetchInfo(cities, language='en', only_collect=False):
   
    cityData = {}
    
    if len(cities) != 1:
        raise ValueError("Incorrect number of cities") 
    for city in cities:
        setupInfoFetchObjects(city, language)
        cityData[city] = populateAttributeMap(city, language)
    
    import pandas as pd
    df = pd.read_csv("dataset.csv")
    columnNames = df.columns
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    with open(os.path.join(os.getcwd(), "cities_tripadvisor.json"), "r") as f:
        tripAdvisorData = json.loads(f.read())
    
    
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [DataOrgainzer] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    if not only_collect:    
        logging.info("*" * 80)
        logging.info("Start: Data Organization")
        logging.info("*" * 80)
        logging.debug("")
        for city in cities:
            logging.info("Oraganizing data for {}".format(city))
            logging.info("Fetching relevant info...")
            logging.info("Deduplicating...")
            time.sleep(2)
            logging.info("Orgainzed Data for {}".format(city))
            row = df.loc[df['city'] == city]
 #            for key in columnNames[2:len(columnNames)-1]:
 #                value = None
 #                if 0 < row[key].values[0] and 2 > row[key].values[0]:
 #                     value = "Poor"
 #                if 2 < row[key].values[0] and 4 > row[key].values[0]:
 #                     value = "Average"
 #                if 4 < row[key].values[0] and 6 > row[key].values[0]:
 #                     value = "Above Average"
 #                if 6 < row[key].values[0] and 8 > row[key].values[0]:
 #                     value = "Good"
 #                else:
 #                     value = "Outstanding"
 #                cityData[city][key] = value
            cityData[city]["Wikipedia Url"] = wikiUrl[0]
            # cityData[city]["cityImage"] = []
            # cityData[city]["cityImage"].append(os.path.join(os.getcwd(), "images_download", "{}_{}.png".format(city, 1)))
            cityData[city]["cityImage"] = os.path.join(os.getcwd(), "cities", "{}.jpg".format(city.replace(" ", "_")))
            cityData[city]["Plan Your Trip At"] = tripAdvisorData[city]
            logging.debug("**** City: {} ****".format(city))
            prettyPrint(cityData[city])
        return cityData[city]


def main():
    
    cities = args.cities
    language = args.lang
    
    cityData = {}
    
      
    for city in cities:
        setupInfoFetchObjects(city, language)
        cityData[city] = populateAttributeMap(city, language)
    
    import pandas as pd
    df = pd.read_csv("dataset.csv")
    columnNames = df.columns
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [DataOrgainzer] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    if not args.only_collect:    
        logging.info("*" * 80)
        logging.info("Start: Data Organization")
        logging.info("*" * 80)
        logging.debug("")
        for city in cities:
            logging.info("Oraganizing data for {}".format(city))
            logging.info("Fetching relevant info...")
            logging.info("Deduplicating...")
            time.sleep(2)
            logging.info("Orgainzed Data for {}".format(city))
            row = df.loc[df['city'] == city]
            for key in columnNames[2:len(columnNames)-1]:
                value = None
                if 0 < row[key].values[0] and 2 > row[key].values[0]:
                     value = "Poor"
                if 2 < row[key].values[0] and 4 > row[key].values[0]:
                     value = "Average"
                if 4 < row[key].values[0] and 6 > row[key].values[0]:
                     value = "Above Average"
                if 6 < row[key].values[0] and 8 > row[key].values[0]:
                     value = "Good"
                else:
                     value = "Outstanding"
                cityData[city][key] = value
            cityData[city]["wikiUrl"] = wikiUrl[0]
            cityData[city]["cityImage"] = []
            cityData[city]["cityImage"].append(os.path.join(os.getcwd(), "images_download", "{}_{}.png".format(city, 1)))
            logging.debug("**** City: {} ****".format(city))
            prettyPrint(cityData[city])


if __name__ == "__main__":
    
    # Setup Logging
    logging.basicConfig(filename="item_collection.log", level=logging.DEBUG, format='[%(asctime)s] [ItemCollector] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.basicConfig(level=logging.INFO)
    
    # Add command line arguments
    parser = argparse.ArgumentParser(description=
        "Web scrapper to fetch info about city")
    parser.add_argument("--cities", type=str, required=True,
                        help="Enter the city name", nargs='+')
    parser.add_argument("--lang", type=str, default='en',
                        help="Language in which information"
                             " about the city to be fetched")
    parser.add_argument("--only_collect", default=False, action="store_true",
                        help="Pass if data organization needs to be skipped") 
    args = parser.parse_args()
 
    main()
