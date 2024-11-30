from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import requests
from bs4 import BeautifulSoup
import json
import re

class BookingScraper:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.soup = None

    def setup_driver(self):
        options = Options()
        options.headless = True
        options.add_argument('--log-level=3')  # Suppress DevTools logging
        service = Service(EdgeChromiumDriverManager().install())
        self.driver = webdriver.Edge(service=service, options=options)

    def clean_json_string(self, json_str):
        # Remove JavaScript-style comments
        json_str = re.sub(r'//.*?\n|/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        # Replace single quotes with double quotes
        json_str = json_str.replace("'", '"')
        
        # Quote unquoted property names
        json_str = re.sub(r'(\s*)(\w+)(\s*:)', r'\1"\2"\3', json_str)
        
        # Remove trailing commas
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        return json_str

    def get_coordinates(self):
        try:
            map_element = self.soup.find('a', id='hotel_address')
            if not map_element:
                return None
                
            coords_str = map_element.get('data-atlas-latlng')
            if not coords_str:
                return None
                
            lat, lng = map(float, coords_str.split(','))
            return {
                'latitude': lat,
                'longitude': lng
            }
            
        except Exception as e:
            print(f"Error extracting coordinates: {str(e)}")
            return None
        
    def get_nearby_places(self):
        try:
            description = self.soup.find('div', class_="bui-grid__column bui-grid__column-8 k2-hp--description")
            if not description:
                return None
            
            # Clean the text by removing quotes and extra spaces
            text = description.text.strip() 
            return text
            
        except Exception as e:
            print(f"Error extracting nearby places: {str(e)}")
            return None
        
    def extract_hotel_amenities(self):
        try:
            amenities = self.soup.find('ul', class_='c807d72881 d1a624a1cc e10711a42e')
            if not amenities:
                return None
                
            amenities_list = [a.text for a in amenities.find_all('li')]
            return amenities_list
            
        except Exception as e:
            print(f"Error extracting amenities: {str(e)}")
            return None

    def extract_hotel_data(self):
        try:
            self.setup_driver()
            self.driver.get(self.url)
            html = self.driver.page_source
            self.soup = BeautifulSoup(html, 'html.parser')

            script_tag = self.soup.find('script', string=lambda t: t and 'window.utag_data' in t)
            if not script_tag:
                raise ValueError("Script tag with utag_data not found")

            json_match = re.search(r'window\.utag_data\s*=\s*({.*?});', script_tag.string, re.DOTALL)
            if not json_match:
                raise ValueError("Could not extract JSON data")

            raw_json = json_match.group(1)
            cleaned_json = self.clean_json_string(raw_json)
            data = json.loads(cleaned_json)
            
            # Get coordinates and add to data
            coordinates = self.get_coordinates()
            if coordinates:
                data.update(coordinates)
           
            nearby_places = self.get_nearby_places()
            if nearby_places:
                data['nearby_places'] = nearby_places

            amnities = self.extract_hotel_amenities()
            if amnities:
                data['amenities'] = amnities

            return data

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return None
        except Exception as e:
            print(f"Error: {str(e)}")
            return None
        finally:
            if self.driver:
                self.driver.quit()

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

    def extract_unit_url(self, json_data):
        try:
            unit_url = json_data['props']['pageProps']['static_data']['data']['items'][0]['url']
            print(f"Unit URL: {unit_url}")
            return unit_url
        except (KeyError, IndexError) as e:
            print(f"Error extracting unit URL: {str(e)}")
            return None

    def extract_unit_data(self, json_data):
        try:
            unit_data = json_data['props']['pageProps']['serverData']['data']
            print(f"Unit Data: {unit_data}")
            amenities = unit_data['extraDescription']
            return {
                'amenities': amenities
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

def main():
    url = 'https://gathern.co/view/16595?srsltid=AfmBOorBI-ZJT9KkXAR_dcLS-mOxxpe48i_KIrqQNZSdIeWwGl5oT6t4'.split("?")[0]
    scraper = GathernScraper(url)
    unit_data = scraper.scrape()

    if unit_data:
        print("Unit Data:")
        print(json.dumps(unit_data, indent=2, ensure_ascii=False))
    else:
        print("Failed to extract unit data")

if __name__ == "__main__":
    main()