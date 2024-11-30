import googlemaps
from googlesearch import search


query = "شاليهات كورنر"

result = []
for j in search(query, num=10, stop=10, pause=2):
    url_name = j.split("/")[2].removeprefix("www.").split(".")[0]
    result.append({"url_name":url_name, "url_full":j})

print(result)

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
            # Use the provided latitude and longitude for Riyadh
            lat, lng = 24.4, 46.71667

            # Search for places based on text query and location
            response = self.client.places(query=query, location=(lat, lng), radius=50000)
            if response['status'] == 'OK':
                places = []
                for place in response['results']:
                    place_id = place['place_id']
                    place_details = self.client.place(place_id=place_id, language='ar')
                    if place_details['status'] == 'OK':
                        details = place_details['result']
                        details['opening_hours'] = details.get('current_opening_hours', {}).get('weekday_text', None)
                        details.pop('current_opening_hours', None)
                        details.pop('adr_address', None)
                        details.pop('address_components', None)
                        places.append(details)
                return places
            else:
                print(f"Error in places search: {response['status']} ({response.get('error_message', 'No error message provided')})")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

# Example usage:
# api_key = 'AIzaSyB1rAHNxzpqmqO009KA7Ck00QYI7875SX0'
# places = GooglePlaces(api_key)
# data = places.get_place_data('chalet')
# import json
# with open('places.json', 'w', encoding='utf-8') as f:
#     json.dump(data, f, indent=4, ensure_ascii=False)
# print(data)