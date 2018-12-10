import argparse
import json
import pprint
import requests
import sys
import urllib
import csv
import json
import time

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

API_KEY="F9hQgNIS11SCU_1DVOFAYHeO06V5KdXeRl3tYs3W7Y41SLgGJQv16Zm3fEBSbqbnRTewddyr7eXPc1KqLfC7ZmV-fHfjBHfmMlK8MN1JaHDJyHoojq2RH7oRK0cJXHYx"
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'

DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'




def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()

def search(api_key, term, location):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'radius': 24000,
        'limit': 50
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)
		
def getRestaurant():
    # gets restaurants
    restaurants = search(API_KEY, 'restaurants', '1201 Massachusetts Ave, Cambridge, MA')['businesses']
    final = []
    num_people = 9
    while num_people > 8:
        num_people = input("How many people are in your group? (8 max) ")
    categories = set()
    for restaurant in restaurants:
        final.append(restaurant['name'])
        for category in restaurant["categories"]:
            categories.add(category['title'].lower())

    # intializes constraints
    distance_constraint = 16090  
    rating_constraint = 0
    price_constraint = 4
    category_constraints = set()
    for restaurant in restaurants:
        if restaurant['is_closed']:
            final.remove(restaurant['name'])


    # gets everyone's constraints
    for i in range(num_people):

        min_rating = input("What is the minimum rating for a restaurant that you are willing to go to? (1.0 - 5.0) ")
        while min_rating < 1.0 or min_rating > 5.0:
            min_rating = input("What is the minimum rating for a restaurant that you are willing to go to? (1.0 - 5.0) ")
        if min_rating > rating_constraint:
            rating_constraint = min_rating

        max_price = input("What is the maximum price range for a restaurant that you are willing to go to? (1 - 4) ")
        while max_price < 1 or max_price > 4: 
            max_price = input("What is the maximum price range for a restaurant that you are willing to go to? (1 - 4) ")
        if max_price < price_constraint:
            price_constraint = max_price

        max_distance = input("How far are you willing to go? ") * 1609 # mile to meter conversion
        if max_distance < distance_constraint:
            distance_constraint = max_distance

        for category in categories:
            print(category)
        print("Here are the categories: please indicate which ones you would not like to go to (press d when done)")
        current_input = raw_input("What is your input? ")
        while not (current_input == 'd' or current_input == 'D'):
            if not (current_input == 'd' or current_input == 'D'):
                category_constraints.add(current_input)
                current_input = raw_input("What is your input? ") 


    # if restaruant violates constraint, restaurant is removed from consideration
    start_time = time.time()
    for restaurant in restaurants:
        if restaurant['distance'] > distance_constraint or restaurant['rating'] < rating_constraint or ('price' in restaurant.keys() and len(restaurant['price']) > price_constraint):
            final.remove(restaurant['name'])
        for category in restaurant["categories"]:
            if category['title'].lower() in category_constraints:
                if restaurant['name'] in final:
                    final.remove(restaurant['name'])
    if len(final) > 0:
        print(final[0])
    print(time.time() - start_time)
getRestaurant()


