import json
import requests
import random
import pandas as pd


def lambda_handler(event, context):

    # inputType = 'genre'
    # inputVal = 'comedy'
    # isRating = 'true'
    # ratingVal = '2.5'
    # amzn_userId = 'Amzn.testID1'

    inputType = event["inputType"]
    inputVal = event["inputVal"]
    isRating = event["isRating"]
    ratingVal = event["ratingVal"]
    amzn_userId = event["userId"]

    # Setting all required urls for cloudsearch
    movies_info_url_beg = "https://search-movies-info-bt4bos5j67ptjvxx5zsl2nhlsm.us-west-2.cloudsearch.amazonaws.com/2013-01-01/search?q="
    ratings_info_url_beg = "https://search-ratings-info-bovd6hhgfjr73x52lcju55ikbq.us-west-2.cloudsearch.amazonaws.com/2013-01-01/search?q="
    url_end_A = "&q.parser=simple&q.options=%7B%22defaultOperator%22%3A%22or%22%2C%22fields%22%3A%5B%22"
    movies_url_end_B = "%22%5D%2C%22operators%22%3A%5B%5D%7D&return=_all_fields%2C_score&sort=_score+desc&size=100"
    ratings_url_end_B = "%22%5D%2C%22operators%22%3A%5B%5D%7D&return=_all_fields%2C_score&sort=_score+desc&size=10000"

    # url for movies-info cloudsearch
    finalURL = movies_info_url_beg + inputVal + url_end_A + inputType + movies_url_end_B
    response = requests.get(finalURL)
    posts = json.loads(response.text) #has 100 movies for given inputType and inputVal

    #if rating val is given, then find avg ratings and return movie which has max avg rating.
    if isRating == "true":

        #string of all movie ids for cloudsearch
        all_movie_id_vals = ""
        for hit in posts["hits"]["hit"]:
            all_movie_id_vals += hit['fields']['movie_id'] + '+'
        #helper variables
        max_avg, max_movie_id, counter, max_counter = 0, -1, 0, -1

        #url for ratings-info cloudsearch
        ratings_full_url = ratings_info_url_beg + all_movie_id_vals + url_end_A + 'movie_id' + ratings_url_end_B
        response = requests.get(ratings_full_url)
        all_ratings = json.loads(response.text) #contains 10000 movies with ~100 ratings each

        #list is for importing to dataframe
        list = []
        for hit in all_ratings['hits']['hit']:
            hit['fields']['user_rating'] = int(hit['fields']['user_rating'])
            list.append(hit['fields'])
        dataframe = pd.DataFrame.from_dict(list)

        #mean_df creation calculates ratings by grouping by movie_id. Columns: movie_id, user_rating
        mean_df = dataframe.groupby('movie_id', as_index=False).mean()

        #finding row value which has highest 'user_rating'
        num = mean_df['user_rating'].argmax()
        #final_movie_id is found by indexing by num
        final_movie_id = mean_df.iloc[num]['movie_id']

        #helper variables
        index, counter = -1, 0
        # finding index value of return movie in posts to get director (and maybe other) info.
        for hit in posts['hits']['hit']:
            if final_movie_id == hit['fields']['movie_id']:
                index = counter
                break
            counter += 1

        #here, movie_rec and director are created if isRating is true
        movie_rec = posts['hits']['hit'][index]['fields']['movie_name']
        director = posts['hits']['hit'][index]['fields']['director']

    #simple rand function to find a random movie from posts if rating is not specified.
    elif isRating == 'false':
        if posts["hits"]["found"] < 100:
            rand_limit = int(posts["hits"]["found"])
        else:
            rand_limit = 100

        rand = random.randint(0,rand_limit)

        #here, movie_rec and director are created if isRating is false
        movie_rec = posts['hits']['hit'][rand]['fields']['movie_name']
        director = posts['hits']['hit'][rand]['fields']['director']

    #creating final speak_output based on inputType
    if inputType == "genre":
        speak_output = 'A good ' + inputVal + ' movie to watch is ' + movie_rec + ', directed by ' + director
        # Ex: A good comedy movie to watch is The Hangover, directed by Todd Phillips
    elif inputType == "director":
        speak_output = "I recommend " + movie_rec  + " directed by " + director + " to you"
        # Ex: I recommend The Hangover which is directed by Todd Phillips to you

    return speak_output
