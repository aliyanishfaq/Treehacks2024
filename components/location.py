import os
from dotenv import load_dotenv
import requests
import googlemaps

load_dotenv()

def location():
    """
    Function returns the current location
    """
    api_key = os.getenv('GOOGLE_MAPS_KEY')
    gmaps = googlemaps.Client(key=api_key)

    data = geolocate(api_key)
    latitude = float(data['location']['lat'])
    longitude = float(data['location']['lng'])

    result = gmaps.reverse_geocode((latitude, longitude))
    if result:
        address = result[0].get('formatted_address', 'No address found')
    else:
        address = 'No address found'
    print(address)
    return address




def geolocate(api_key):
    """
    Function takes in the api_key and returns coordinates
    """
    url = "https://www.googleapis.com/geolocation/v1/geolocate"
    params = {'key': api_key}
    headers = {'Content-Type': 'application/json'}
    data = {
        "homeMobileCountryCode": 310,
        "homeMobileNetworkCode": 410,
        "radioType": "gsm",
        "carrier": "Vodafone",
        "considerIp": "true"
    }

    response = requests.post(url, params=params, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error in geolocation request: {response.text}")



# Example usage
if __name__ == "__main__":
    location()