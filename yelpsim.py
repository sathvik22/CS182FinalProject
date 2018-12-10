import argparse
import json
import pprint
import requests
import sys
import urllib
import csv
import json
import random
import math
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

# category assignments
categories = {'bars' : 1, 'lounges' : 1, 'wine bars' : 1, 'beer, wine & spirits' : 1,
 'pubs' : 1, 'beer bar' : 1, 'cocktail bars' : 1, 'mediterranean' : 2, 'turkish' : 2,
  'greek' : 2, 'italian' : 2, 'japanese' : 3, 'mongolian' : 3, 'noodles' : 3,
   'sushi bars' : 3, 'poke' : 3, 'korean' : 3, 'hot pot' : 3, 'thai' : 3, 'thai' : 3,
    'ramen' : 3, 'bubble tea' : 3, 'izakaya' : 3, 'vietnamese' : 3, 'american (new)' : 4,
     'cajun/creole' : 4, 'sandwiches' : 4, 'barbeque' : 4, 'southern' : 4, 'salad' : 4,
      'breakfast & brunch' : 4, 'american (traditional)' : 4, 'seafood' : 4, 'burgers' : 4,
       'pizza' : 4, 'mexican' : 5, 'peruvian' : 5, 'latin american' : 5, 'spanish' : 5,
        'tapas/small plates' : 5, 'tapas bars' : 5, 'brazilian' : 5, 'venezuelan' : 5,
         'pop-up restaurants' : 6, 'desserts' : 6, 'middle eastern' : 6,
          'venues & event spaces' : 6, 'tea rooms' : 6, 'indian' : 3, 'asian fusion' : 3, 'chinese' : 3, 'szechuan' : 3, 
          'himalayan/nepalese' : 3, 'african' : 6}


# calculates euclidian distance between two restaurants
def calculate_distance(a, b):
    rating_distance = abs(a["rating"] - b["rating"])
    distance_distance = abs(a["distance"] - b["distance"])
    price_distance = 0
    if "price" in a.keys() and "price" in b.keys():
        price_distance = abs(len(a["price"]) - len(b["price"]))
    category_distance = 0
    category_a = a["categories"][0]['title'].lower()
    category_b = b["categories"][0]['title'].lower()
    if category_a not in categories:
        categories[category_a] = 6    
    if category_b not in categories:
        categories[category_b] = 6
    if category_a == category_b:
        category_distance = 0
    elif categories[category_a] == categories[category_b]:
        category_distance = 1
    else:
        category_distance = 2
    total_distance = rating_distance + distance_distance + price_distance + category_distance
    return total_distance


# gets closest neighbor of restaurant
def neighbor_restaurant(restaurant, restaurants):
    closest_neighbors = []
    min_distance = 999999
    for rest in restaurants:
            temp_d = calculate_distance(restaurant, rest)
            if temp_d < min_distance:
                min_distance = temp_d
            closest_neighbors.append(rest)
    if restaurant in closest_neighbors:
        closest_neighbors.remove(restaurant)
    closest_neighbors2 = sorted(closest_neighbors)
    closest_neighbors3 = closest_neighbors2[1:10]


    val = random.choice(closest_neighbors3)

    
    return val

def sim_a():
    TRIALS = 1000
    T = 1000.0
    DECAY = 0.98


    restaurants = search(API_KEY, 'restaurants', '1201 Massachusetts Ave, Cambridge, MA')['businesses']

    num_people = 9
    while num_people > 8:
        num_people = input("How many people are in your group? (8 max) ")
    categories = set()
    for restaurant in restaurants:
        for category in restaurant["categories"]:
            categories.add(category['title'].lower())

    # initialize contraints
    distance_constraint = 16090  
    rating_constraint = 0
    price_constraint = 4
    category_constraints = set()
    preferred_categories = set()

    # gets constraints from everyone in group
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
        print("Please indicate which ones you would like to go to (press d when done)")
        current_input = raw_input("What is your input? ")
        while not (current_input == 'd' or current_input == 'D'):
            if not (current_input == 'd' or current_input == 'D'):
                preferred_categories.add(current_input)
                current_input = raw_input("What is your input? ") 



    # simulated annealing
    start_time = time.time()
    sim_rest = random.choice(restaurants)
    for trial in range(TRIALS):
        next_rest = neighbor_restaurant(sim_rest, restaurants)
        sim_val = 0
        next_val = 0
        # calculates values for old and neighbor restaurants
        if sim_rest['distance'] > distance_constraint:
            sim_val += 1
        if sim_rest['rating'] < rating_constraint:
            sim_val += 1
        if 'price' in sim_rest.keys():
            if len(sim_rest['price']) > price_constraint:
                sim_val += 1
        for category in sim_rest["categories"]:
            if category['title'].lower() in category_constraints:
                sim_val += 1
            if category['title'].lower() in preferred_categories:
                sim_val -= 1

        if next_rest['distance'] > distance_constraint:
            next_val += 1
        if next_rest['rating'] < rating_constraint:
            next_val += 1
        if 'price' in next_rest.keys():
            if len(next_rest['price']) > price_constraint:
                next_val += 1
        for category in next_rest["categories"]:
            if category['title'].lower() in category_constraints:
                next_val += 1
            if category['title'].lower() in preferred_categories:
                next_val -= 1


        # switches to neighbor if it is better or if it is worse with probability proportional to T
        try:
            ans = math.exp((next_val - sim_val) / T)
        except OverflowError:
            ans = float('inf')

        if next_val < sim_val:
            sim_rest = next_rest
        
        elif next_val >= sim_val and random.randint(1, 100) <= ans:
            sim_rest = next_rest
          

        T *= DECAY
    print(sim_rest['name'])
    print(time.time() - start_time)



sim_a()














