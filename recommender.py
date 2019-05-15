import data
from data import CITIES, BUSINESSES, USERS, REVIEWS, TIPS, CHECKINS
from geopy import distance

import random
import pandas as pd
import numpy as np


# TODO!!
def maths():
    """
    Does some calculations for the recommender functions.
    """
    if user_id is not None:
        " Returns all reviews from a user "
        reviews = []
        for city in REVIEWS:
            review = pd.DataFrame.from_dict(REVIEWS[city])
            reviews.append(review)
        reviews = pd.concat(reviews, ignore_index=True)
        reviews = reviews[reviews['user_id'] == user_id]

        " Returns all other businesses in given city in a dataframe "
        other_businesses = []
        for city in BUSINESSES:
            business = pd.DataFrame.from_dict(BUSINESSES[city])
            other_businesses.append(business)
        other_businesses = pd.concat(other_businesses, ignore_index=True)

        " Returns businesses that user reviewed and calculates which city appears most. "
        bedrijven = pd.merge(reviews, other_businesses, on=['business_id'], how='inner')
        city_counts = bedrijven['city'].value_counts()
        max_city = city_counts.idxmax().lower()


def recommend_home(user_id=None, n=10):
    """
    Returns n recommendations as a list of dicts.
    Optionally takes in a user_id.
    A recommendation is a dictionary in the form of:
        {
            business_id:str
            stars:str
            name:str
            city:str
            adress:str
        }
    """

    if user_id is not None:
        " Returns all reviews from a user "
        reviews = []
        for city in REVIEWS:
            review = pd.DataFrame.from_dict(REVIEWS[city])
            reviews.append(review)
        reviews = pd.concat(reviews, ignore_index=True)
        reviews = reviews[reviews['user_id'] == user_id]

        " Returns all other businesses in given city in a dataframe "
        other_businesses = []
        for city in BUSINESSES:
            business = pd.DataFrame.from_dict(BUSINESSES[city])
            other_businesses.append(business)
        other_businesses = pd.concat(other_businesses, ignore_index=True)

        " Returns businesses that user reviewed and calculates which city appears most. "
        bedrijven = pd.merge(reviews, other_businesses, on=['business_id'], how='inner')
        city_counts = bedrijven['city'].value_counts()
        max_city = city_counts.idxmax().lower()


        highest_scored = sorted(BUSINESSES[max_city], key=lambda x: x['stars'], reverse=True)[:10]
        return highest_scored

    else:
        city = random.choice(CITIES)

    return random.sample(BUSINESSES[city], n)


def recommend_carousel(user_id=None, n=10):
    """
    Returns n recommendations as a list of dicts.
    Optionally takes in a user_id.
    A recommendation is a dictionary in the form of:
        {
            business_id:str
            stars:str
            name:str
            city:str
            adress:str
        }
    """

    if user_id is not None:
        " Returns all reviews from a user "
        reviews = []
        for city in REVIEWS:
            review = pd.DataFrame.from_dict(REVIEWS[city])
            reviews.append(review)
        reviews = pd.concat(reviews, ignore_index=True)
        reviews = reviews[reviews['user_id'] == user_id]

        " Returns all other businesses in given city in a dataframe "
        other_businesses = []
        for city in BUSINESSES:
            business = pd.DataFrame.from_dict(BUSINESSES[city])
            other_businesses.append(business)
        other_businesses = pd.concat(other_businesses, ignore_index=True)

        " Returns businesses that user reviewed and calculates which city appears most. "
        bedrijven = pd.merge(reviews, other_businesses, on=['business_id'], how='inner')
        city_counts = bedrijven['city'].value_counts()
        max_city = city_counts.idxmax().lower()


        random_shops = random.sample(BUSINESSES[max_city], n)
        return random_shops

    else:
        city = random.choice(CITIES)

    return random.sample(BUSINESSES[city], n)


def recommend(user_id=None, business_id=None, city=None, n=10):
    """
    Returns n recommendations as a list of dicts.
    Optionally takes in a user_id, business_id and/or city.
    A recommendation is a dictionary in the form of:
        {
            business_id:str
            stars:str
            name:str
            city:str
            adress:str
        }
    """
    if city is not None and business_id is not None:
        " Returns all other businesses in given city in a dataframe "
        other_businesses = []
        for city in BUSINESSES:
            business = pd.DataFrame.from_dict(BUSINESSES[city])
            other_businesses.append(business)
        other_businesses = pd.concat(other_businesses, ignore_index=True)
        other_businesses = pd.concat([other_businesses.drop(['attributes'], axis=1), other_businesses['attributes'].apply(pd.Series)], axis=1)
        other_businesses_categories = extract_categories(other_businesses)

        " Makes pivot table of other businesses based on categories "
        other_businesses_pivot = pivot_categories(other_businesses_categories)

        " Makes similarity matrix based on pivot table "
        other_businesses_similarity = create_similarity_matrix_categories(other_businesses_pivot)

        " Gives back a series of businesses that look most like the chosen business without business itself"
        look_a_likes = other_businesses_similarity[business_id].loc[(other_businesses_similarity[business_id] > 0.3)].drop(business_id)

        lijst = other_businesses[other_businesses.business_id.isin(look_a_likes.index)]

        """
        Looks for latitude and longitude for each shop in the list
        and calculates distance between chosen shop and shop in list.
        Gives it a new column 'distance' in lijst.
        """
        distances = []
        for shop in lijst.index:
            lat = lijst.loc[shop]['latitude']
            lon = lijst.loc[shop]['longitude']

            chosen_lat = other_businesses.loc[other_businesses['business_id']==business_id, 'latitude'].item()
            chosen_lon = other_businesses.loc[other_businesses['business_id']==business_id,'longitude'].item()

            distance = calculate_distance(lat, lon, chosen_lat, chosen_lon)
            distances.append(distance)
        lijst['distance'] = distances

        " Removes shops with distances bigger than 100 km and sorts dataframe based on distance. "
        lijst = lijst[lijst['distance'] <= 100].sort_values('distance')

        " Makes list of dicts from dataframe so it can be returned. "
        lijst = lijst.T.to_dict().values()
        return lijst

    if not city:
        city = random.choice(CITIES)

    return random.sample(BUSINESSES[city], n)


def extract_categories(businesses):
    """Create an unfolded genre dataframe. Unpacks categories seprated by a ',' into seperate rows.

    Arguments:
    movies -- a dataFrame containing at least the columns 'business_id' and 'categories'
              where categories are seprated by ','
    """
    categories_m = businesses.apply(lambda row: pd.Series([row['business_id']] + row['categories'].lower().split(",")), axis=1)
    stack_categories = categories_m.set_index(0).stack()
    df_stack_categories = stack_categories.to_frame()
    df_stack_categories['business_id'] = stack_categories.index.droplevel(1)
    df_stack_categories.columns = ['categories', 'business_id']
    return df_stack_categories.reset_index()[['business_id', 'categories']]


def pivot_categories(df):
    """Create a one-hot encoded matrix for categories.

    Arguments:
    df -- a dataFrame containing at least the columns 'business_id' and 'categories'

    Output:
    a matrix containing '0' or '1' in each cell.
    1: the shop has the category
    0: the shop does not have the category
    """
    return df.pivot_table(index = 'business_id', columns = 'categories', aggfunc = 'size', fill_value=0)


def create_similarity_matrix_categories(matrix):
    """Create a  """
    npu = matrix.values
    m1 = npu @ npu.T
    diag = np.diag(m1)
    m2 = m1 / diag
    m3 = np.minimum(m2, m2.T)
    return pd.DataFrame(m3, index = matrix.index, columns = matrix.index)


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculates distance between two given sets of latitude and longitude
    according to geopy calculations.
    """
    coords_1 = (lat1, lon1)
    coords_2 = (lat2, lon2)

    return distance.distance(coords_1, coords_2).km
