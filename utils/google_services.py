import googlemaps
from googlesearch import search
from utils import haversine
from scraper import GathernScraper
import json

class GoogleSearch:
    def __init__(self, query:str, num:int, stop:int, pause:int) -> None:
        self.query = query
        self.num = num
        self.stop = stop
        self.pause = pause

    def search(self) -> list:
        result = []
        for j in search(self.query, num=self.num, stop=self.stop, pause=self.pause):
            url_name = j.split("/")[2].removeprefix("www.").split(".")[0]
            result.append({"url_name":url_name, "url_full":j})
        return result


class GooglePlaces:
    def __init__(self, api_key):
        self.client = googlemaps.Client(key=api_key)

    def get_place_data(self, query):
        try:
            lat, lng = 24.7540383, 46.8670658
            places = []
            page_token = None

            while True:
                response = self.client.places(query=query, location=(lat, lng), radius=11, page_token=page_token)
                if response['status'] == 'OK':
                    for place in response['results']:
                        query = place['name'] + ' ' + place['formatted_address']
                        search_result = GoogleSearch(place['name'], 10, 10, 2).search()
                        gathern_index = next((i for i, item in enumerate(search_result) if item['url_name'] == 'gathern'), None)

                        if gathern_index is not None:
                            print(f"Gathern was found. The full url is {search_result[gathern_index]['url_full']}")
                        else:
                            print("Gathern was not found.")

                        place_id = place['place_id']
                        place_details = self.client.place(place_id=place_id, language='ar')
                        if place_details['status'] == 'OK':
                            details = place_details['result']
                            details['opening_hours'] = details.get('current_opening_hours', {}).get('weekday_text', None)
                            details.pop('current_opening_hours', None)
                            details.pop('adr_address', None)
                            # details.pop('address_components', None)
                            try:
                                if gathern_index is not None:
                                    gathern_url = search_result[gathern_index]['url_full']
                                    scraper = GathernScraper(gathern_url)
                                    unit_data = scraper.scrape()
                                    distance = haversine([place['geometry']['location']['lat'], place['geometry']['location']['lng']], unit_data['latLng'])
                                    if distance and distance <= 10:
                                        print(f"The place of {gathern_url} is within 10 km: {place['name']}. Data is added in the json file.")
                                        place.update(unit_data)
                                    else:
                                        print(f"The place of {gathern_url} is not within 10 km: {place['name']}. Hence, the data is not added in the json file.")
                                        continue
                                places.append(place)
                            except Exception as e:
                                print(f"An error occurred: {e}")
                                continue

                    page_token = response.get('next_page_token')
                    if not page_token or len(places) >= 800:
                        break

                    import time
                    time.sleep(2)
                else:
                    print(f"Error in places search: {response['status']} ({response.get('error_message', 'No error message provided')})")
                    break

            return places
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

# Example usage:
api_key = 'AIzaSyB1rAHNxzpqmqO009KA7Ck00QYI7875SX0'
places = GooglePlaces(api_key)
data = places.get_place_data('chalet')

with open('places.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
print(f"Data has been saved to places.json with {len(data)} entries.")