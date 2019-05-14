import data
from data import CITIES, BUSINESSES, USERS, REVIEWS, TIPS, CHECKINS

import random
import pandas as pd
import numpy as np

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
        print(other_businesses)
        other_businesses_categories = extract_categories(other_businesses)

        " Makes pivot table of other businesses based on categories "
        other_businesses_pivot = pivot_categories(other_businesses_categories)

        " Makes similarity matrix based on pivot table "
        other_businesses_similarity = create_similarity_matrix_categories(other_businesses_pivot)

        " Gives back a series of businesses that look most like the chosen business without business itself"
        look_a_likes = other_businesses_similarity[business_id].loc[(other_businesses_similarity[business_id] > 0.3)].drop(business_id)
        print(look_a_likes)

        lijst = other_businesses[other_businesses.business_id.isin(look_a_likes.index)]
        print(lijst)
    if not city:
        city = random.choice(CITIES)
    
    return random.sample(BUSINESSES[city], n)

def extract_categories(businesses):
    """Create an unfolded genre dataframe. Unpacks genres seprated by a '|' into seperate rows.

    Arguments:
    movies -- a dataFrame containing at least the columns 'movieId' and 'genres' 
              where genres are seprated by '|'
    """
    categories_m = businesses.apply(lambda row: pd.Series([row['business_id']] + row['categories'].lower().split(",")), axis=1)
    stack_genres = categories_m.set_index(0).stack()
    df_stack_genres = stack_genres.to_frame()
    df_stack_genres['business_id'] = stack_genres.index.droplevel(1)
    df_stack_genres.columns = ['categories', 'business_id']
    return df_stack_genres.reset_index()[['business_id', 'categories']]


def pivot_categories(df):
    """Create a one-hot encoded matrix for genres.
    
    Arguments:
    df -- a dataFrame containing at least the columns 'movieId' and 'genre'
    
    Output:
    a matrix containing '0' or '1' in each cell.
    1: the movie has the genre
    0: the movie does not have the genre
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

#def calculate_distance(series, business):
 #   """ Calculate distance between chosen business and businesses that look a like """
  #  lijst = []
   # for item in series:
    #    i = BUSINESSES['item']
     #   print(i)
        