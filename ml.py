#from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import numpy as np
import itertools
import string
import json
import boto3
import requests
#session = boto3.session.Session()
#credentials = session.get_credentials()
from boto3.dynamodb.conditions import Key, LessThan
#from sklearn.svm import SVC, LinearSVC
#from sklearn.model_selection import StratifiedKFold
#from sklearn import metrics
#from matplotlib import pyplot as plt; plt.rcdefaults()

from helper import *
#import pandas as pd
#import numpy as np
def main():
    movieurl = "https://search-movies-info-bt4bos5j67ptjvxx5zsl2nhlsm.us-west-2.cloudsearch.amazonaws.com/2013-01-01/search?q=comedy%7C-comedy&q.parser=simple&q.options=%7B%22defaultOperator%22%3A%22and%22%2C%22fields%22%3A%5B%22genre%22%5D%2C%22operators%22%3A%5B%22and%22%2C%22escape%22%2C%22fuzzy%22%2C%22near%22%2C%22not%22%2C%22or%22%2C%22phrase%22%2C%22precedence%22%2C%22prefix%22%2C%22whitespace%22%5D%7D&return=_all_fields%2C_score&highlight.director=%7B%22max_phrases%22%3A3%2C%22format%22%3A%22text%22%2C%22pre_tag%22%3A%22*%23*%22%2C%22post_tag%22%3A%22*%25*%22%7D&highlight.genre=%7B%22max_phrases%22%3A3%2C%22format%22%3A%22text%22%2C%22pre_tag%22%3A%22*%23*%22%2C%22post_tag%22%3A%22*%25*%22%7D&highlight.movie_id=%7B%22max_phrases%22%3A3%2C%22format%22%3A%22text%22%2C%22pre_tag%22%3A%22*%23*%22%2C%22post_tag%22%3A%22*%25*%22%7D&highlight.movie_name=%7B%22max_phrases%22%3A3%2C%22format%22%3A%22text%22%2C%22pre_tag%22%3A%22*%23*%22%2C%22post_tag%22%3A%22*%25*%22%7D&highlight.release_date=%7B%22max_phrases%22%3A3%2C%22format%22%3A%22text%22%2C%22pre_tag%22%3A%22*%23*%22%2C%22post_tag%22%3A%22*%25*%22%7D&sort=_score+desc&size=8186"
    ratingurl_beg = "https://search-ratings-info-bovd6hhgfjr73x52lcju55ikbq.us-west-2.cloudsearch.amazonaws.com/2013-01-01/search?q=9131%7C-9131&cursor="
    cursor = 'initial'
    ratingurl_end = "&return=_all_fields%2C_score&highlight.movie_id=%7B%22max_phrases%22%3A3%2C%22format%22%3A%22text%22%2C%22pre_tag%22%3A%22*%23*%22%2C%22post_tag%22%3A%22*%25*%22%7D&highlight.user_id=%7B%22max_phrases%22%3A3%2C%22format%22%3A%22text%22%2C%22pre_tag%22%3A%22*%23*%22%2C%22post_tag%22%3A%22*%25*%22%7D&highlight.user_rating=%7B%22max_phrases%22%3A3%2C%22format%22%3A%22text%22%2C%22pre_tag%22%3A%22*%23*%22%2C%22post_tag%22%3A%22*%25*%22%7D&sort=_score+desc&size=10000"
    response = requests.get(movieurl)
    moviedb = json.loads(response.text)
    #print(response['hits']['cursor'])
    resp = requests.get(ratingurl_beg + cursor + ratingurl_end)
    ratingdb = json.loads(resp.text)
    ratingdf = []
    count = 1
    while len(ratingdf) < 810001:
        for hit in ratingdb["hits"]["hit"]:
            ratingdf.append(hit["fields"])
        cursor = ratingdb['hits']['cursor']
        if len(ratingdf) == 813317:
            break

        ratingdb.clear()
        resp = requests.get(ratingurl_beg + cursor + ratingurl_end)
        ratingdb = json.loads(resp.text)
        count += 1
    ratingdf = pd.DataFrame(ratingdf) 
#    ratingdf['user_rating'] = pd.to_numeric(ratingdf['user_rating'])
#    ratingdf['user_id'] = pd.to_numeric(ratingdf['user_id'])
    allMovies = []
    for hit in moviedb["hits"]["hit"]:
        allMovies.append(hit["fields"])
    moviedf = pd.DataFrame(allMovies)
#    moviedf['movie_id'] = pd.to_numeric(moviedf['movie_id'])
    #print('Dataset 1 shape: {}'.format(df.shape))
    #print(ratingdf)
    
    #for each in moviedf:
        #print(each["movie_name"])
    #print(ratingdf["hits"]["hit"])
    userInput = [
        {'movie_name':'Scrooged', 'user_rating':5},
        {'movie_name': "Little Big League", 'user_rating':4}
    ]
    inputMovies = pd.DataFrame(userInput)
    inputId = moviedf[moviedf["movie_name"].isin(inputMovies["movie_name"].tolist())]
    #print(inputId)
    inputMovies = pd.merge(inputId, inputMovies)
    userSubset = ratingdf[ratingdf["movie_id"].isin(inputMovies["movie_id"].tolist())]

    userSubsetGroup = userSubset.groupby(['user_id'])
    userSubsetGroup = sorted(userSubsetGroup,  key=lambda x: len(x[1]), reverse=True)
    pearsonCorrelationDict = {}


    #For every user group in our subset
    userSubsetGroup = userSubsetGroup[0:100]
    for name, group in userSubsetGroup:
        
        #Let's start by sorting the input and current user group so the values aren't mixed up later on
#        group['movie_id'] = pd.to_numeric(group['movie_id'])
#        group['user_rating'] = pd.to_numeric(group['user_rating'])
        
        group = group.sort_values(by='movie_id')
        inputMovies = inputMovies.sort_values(by='movie_id')
        
        #Get the N (total similar movies watched) for the formula 
        nRatings = len(group)
        
        #Get the review scores for the movies that they both have in common
        temp_df = inputMovies[inputMovies['movie_id'].isin(group['movie_id'].tolist())]
        temp_df['user_rating'] = pd.to_numeric(temp_df['user_rating'])
        temp_df['movie_id'] = pd.to_numeric(temp_df['movie_id'])
        ###For Debugging Purpose
        #if nRatings<5:
        #    print(inputMovies['movieId'].isin(group['movieId'].tolist()))
        #    break
        #else:
        #    continue
        
        #And then store them in a temporary buffer variable in a list format to facilitate future calculations
        
        tempRatingList = temp_df['user_rating'].tolist()
        
        
        #tempRatingList['user_rating'] = pd.to_numeric(tempRatingList['user_rating'])
        
        #Let's also put the current user group reviews in a list format
        
        tempGroupList = group['user_rating'].tolist()
        for i in range(0, len(tempGroupList)):
            tempGroupList[i] = int(tempGroupList[i])
        #Now let's calculate the pearson correlation between two users, so called, x and y

        #For package based
        #scipy.stats import pearsonr
        #pearsonr(tempRatingList,tempGroupList)[0]

        #For hard code based
        Sxx = sum([i**2 for i in tempRatingList]) - pow(sum(tempRatingList),2)/float(nRatings)
        Syy = sum([i**2 for i in tempGroupList]) - pow(sum(tempGroupList),2)/float(nRatings)
        Sxy = sum( i*j for i, j in zip(tempRatingList, tempGroupList)) - sum(tempRatingList)*sum(tempGroupList)/float(nRatings)


        #If the denominator is different than zero, then divide, else, 0 correlation.
        if Sxx != 0 and Syy != 0:
            pearsonCorrelationDict[name] = Sxy/np.sqrt(Sxx*Syy)
        else:
            pearsonCorrelationDict[name] = 0
    


    pearsonDF = pd.DataFrame.from_dict(pearsonCorrelationDict, orient='index')

    pearsonDF.columns = ['similarityIndex']
    pearsonDF['user_id'] = pearsonDF.index
    pearsonDF.index = range(len(pearsonDF))

    topUsers=pearsonDF.sort_values(by='similarityIndex', ascending=False)[0:50]

    topUsersRating = topUsers.merge(ratingdf, left_on='user_id', right_on='user_id', how='inner')

    #Multiplies the similarity by the user's ratings
    topUsersRating['similarityIndex'] = pd.to_numeric(topUsersRating['similarityIndex'])
    topUsersRating['user_rating'] = pd.to_numeric(topUsersRating['user_rating'])
    topUsersRating['weightedRating'] = topUsersRating['similarityIndex']*topUsersRating['user_rating']


    #Applies a sum to the topUsers after grouping it up by userId
    tempTopUsersRating = topUsersRating.groupby('movie_id').sum()[['similarityIndex','weightedRating']]
    tempTopUsersRating.columns = ['sum_similarityIndex','sum_weightedRating']
    tempTopUsersRating['sum_similarityIndex'] = pd.to_numeric(tempTopUsersRating['sum_similarityIndex'])
    tempTopUsersRating['sum_weightedRating'] = pd.to_numeric(tempTopUsersRating['sum_weightedRating'])

    #Creates an empty dataframe
    recommendation_df = pd.DataFrame()
    #Now we take the weighted average
    recommendation_df['weighted average recommendation score'] = tempTopUsersRating['sum_weightedRating']/tempTopUsersRating['sum_similarityIndex']
    recommendation_df['movie_id'] = tempTopUsersRating.index

    recommendation_df = recommendation_df.sort_values(by='weighted average recommendation score', ascending=False)

    #recommendation_df= recommendation_df['movie_id'].apply(str)
    #moviedf[moviedf['movie_id'].isin(recommendation_df.head(20)['movie_id'].tolist())]
    print(moviedf[moviedf['movie_id'].isin(recommendation_df.head(20)['movie_id'].tolist())])
    return
    

if __name__ == '__main__':
    main()
