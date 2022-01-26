# Movie Recommendation System

## Summary
The recommender system recommends movies from a large collection based on user preferences. Users can specify their individual needs by specifying that they would like to narrow their recommendation by the genre, director, actors and year released.

The system recommends movies using the collaborative filtering model.

Interaction with the front end is done through Alexa Skills Kit which transmits the slot values to Lamba, API Gateway and Cloudsearch. Users cab specify 

A typical conversation with the Alexa interface might look like this:

User: Alexa, give me a movie recommendation

Alexa: Would you like to narrow your recommendation down by genre, director, or actor?

User: Genre

Alexa: What genre/genres would you like?

User: Recommend a horror and thriller movie with a rating of 8 and above

## Dataset
The final dataset is a combination of the [iMDB] (https://datasets.imdbws.com/) and [Netflix dataset] (https://www.kaggle.com/netflix-inc/netflix-prize-data?select=README)

iMDB provides multiple publicly available datasets. We used the following datasets:

- title.basics.tsv.gz (Contains information about movie titles)
- title.crew.tsv.gz (Contains information about directors and writers) 
- name.basics.tsv.gz (Contains further details about directors)

## Contributions
[Dhruv Tiwari]
[Anirudh Gadiraju]
[Rohan Sharma]
