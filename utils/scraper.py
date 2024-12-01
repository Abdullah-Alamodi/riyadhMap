import requests
from bs4 import BeautifulSoup
import json

class GathernScraper:
    def __init__(self, url):
        self.url = url
        self.soup = None

    def fetch_page(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to fetch page: {response.status_code}")
            return None

    def parse_json_data(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')
        if script_tag:
            json_data = json.loads(script_tag.string)
            return json_data
        else:
            print("JSON data not found in the script tag")
            return None
    
    def find_key(self, data, target_key):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == target_key:
                    return value
                elif isinstance(value, (dict, list)):
                    result = self.find_key(value, target_key)
                    if result:
                        return result
        elif isinstance(data, list):
            for item in data:
                result = self.find_key(item, target_key)
                if result:
                    return result
        return None

    def extract_unit_url(self, json_data):
        try:
            unit_url = self.find_key(json_data, 'url')
            if unit_url:
                return unit_url
            else:
                print("Unit URL not found in JSON data")
                return None
        except Exception as e:
            print(f"Error extracting unit URL: {str(e)}")

    def extract_unit_data(self, json_data):
        try:
            unit_data = json_data['props']['pageProps']['serverData']['data']
            amenities_list = [item for amenity in unit_data['extraDescription'] 
                     for item in amenity['content'] 
                     if amenity['content']]
            lat = float(unit_data['chalet']['lat'])
            lng = float(unit_data['chalet']['lng'])
            return {
                'description': unit_data['description'],
                'city_name': unit_data['address']['city'],
                'area_name': unit_data['address']['area'],
                'price': unit_data['normal_price'],
                'url': unit_data['url'],
                'checkinHour': unit_data['checkinHour'],
                'checkoutHour': unit_data['checkoutHour'],
                'reserve_conditions': unit_data['reserve_conditions'],
                'latLng' : (lat, lng),
                'amenities': amenities_list,
                'images': unit_data['gallery']
            }
        except (KeyError, IndexError) as e:
            print(f"Error extracting unit data: {str(e)}")
            return None

    def scrape(self):
        content = self.fetch_page(self.url)
        if not content:
            return None

        json_data = self.parse_json_data(content)
        if not json_data:
            return None

        if '/unit/' not in self.url:
            unit_url = self.extract_unit_url(json_data)
            if not unit_url:
                return None

            unit_content = self.fetch_page(unit_url)
            if not unit_content:
                return None

            unit_json_data = self.parse_json_data(unit_content)
            if not unit_json_data:
                return None

            unit_data = self.extract_unit_data(unit_json_data)
            return unit_data
        else:
            unit_data = self.extract_unit_data(json_data)
            return unit_data

# TODO: user any hotels api to get hotels and resotrs data in Riyadh