# SI 507 Final Project
#Devon Farrell

import requests, csv
import json
from bs4 import BeautifulSoup
import time, sqlite3
import sys
import plotly.graph_objects as go
import secrets_final as secrets
import flask 
from flask import Flask, render_template, json, request
import os

app = Flask(__name__)

key = secrets.API_KEY

CACHE_FILE_NAME = 'movie.json'
CACHE_DICT = {}


#Caching 

def open_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

    

def make_url_request_using_cache(url, cache):
    if url in cache.keys(): # the url is our unique key
        #print("Using cache")
        return cache[url]
    else:
        #print("Fetching")
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

#Movie Information from IMDB Two different ways for different information# 

movie_star = []
movie_director = []

url_250 = 'https://www.imdb.com/chart/top?ref_=nv_mv_250' 
url = make_url_request_using_cache(url_250, CACHE_DICT)
soup_main = BeautifulSoup(url, 'html.parser')
movie_list = soup_main.find_all(class_ = 'posterColumn')
movie_dict = {}
for movie in movie_list:
    url_suffix = movie.find('a')['href']
    full_link = 'https://www.imdb.com' + url_suffix
    img_prep = movie.find('img')
    movie_name = img_prep.get('alt', '')
    movie_dict[movie_name] = {}
    movie_dict[movie_name]['full_link'] = full_link
    movie_dict[movie_name]['movie_name'] = movie_name
    ranking = movie.find("span").attrs['data-value']
    movie_dict[movie_name]['ranking'] = ranking

for movie in movie_dict:
    movie_content = make_url_request_using_cache(movie_dict[movie]['full_link'], CACHE_DICT) 
    movie_content = BeautifulSoup(movie_content, 'html.parser')
    merge = json.loads("".join(movie_content.find("script",{"type":"application/ld+json"}).contents))
    movie_dict[movie]['average_rating'] = merge['aggregateRating']['ratingValue'] 
    movie_dict[movie]['year_published'] = merge['datePublished'][0:4]
    try:
        movie_dict[movie]['content_rating'] = merge['contentRating']
    except:
        movie_dict[movie]['content_rating'] = 'NA'

# get actor and directors
    for star in merge['actor']:
        movie_star.append([movie,star['name']])
    try:
        movie_director.append([movie,merge['director']['name']])  
    except:
        for info in merge['director']:
            movie_director.append([movie,info['name']])     

  

# Summaries for Movie Poster Flask App  

base_url_other = 'https://api.tmdb.org/3/discover/movie/?api_key='+key

#Database Creation 

DBNAME = 'movie_information.sqlite'

def init_db():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    drop_movie = '''
        DROP TABLE IF EXISTS 'Movies';
    '''

    drop_star = '''
        DROP TABLE IF EXISTS 'Stars';

    '''

    drop_director = '''
        DROP TABLE IF EXISTS 'Directors';

    '''
    drop_csv = '''

        DROP TABLE IF EXISTS 'Additional_Movies';

    '''
    drop_additional_ratings = '''

        DROP TABLE IF EXISTS 'Additional_Movies_Ratings';

    '''

    create_stars = '''

        CREATE TABLE 'Stars' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'MovieName' TEXT NOT NUll, 
            'ActorName' TEXT NOT NUll
        );

    '''

    create_director = '''

        CREATE TABLE 'Directors' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT, 
            'MovieName' TEXT NOT NULL, 
            'DirectorName' TEXT NOT NULL 
        );
    '''

    create_movie = '''
        
        CREATE TABLE 'Movies' (
                'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
                'Title' TEXT NOT NULL,
                'Ranking' INTEGER NOT NULL,
                'Year' INTEGER NOT NULL,
                'AverageRating' REAL NOT NULL,
                'ContentRating' TEXT NOT NULL
        );
    '''

    create_additional_ratings = '''

    CREATE TABLE 'Additional_Movies_Ratings' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT, 
        'movie_id' TEXT NOT NULL,
        'total_votes' INTEGER NOT NULL, 
        'mean_votes' INTEGER NOT NULL,
        'median_votes' INTEGER NOT NULL,
        'male_votes' INTEGER NOT NULL,
        'female_votes' INTEGER NOT NULL
    );

    '''

    create_additional_movies = '''

        CREATE TABLE 'Additional_Movies' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            'movie_id' TEXT NOT NULL,
            'Title' TEXT NOT NULL,
            'Years' INTEGER NOT NULL, 
            'data_published' REAl NOT NULL, 
            'genre' TEXT NOT NULL,
            'duration' INTEGER NOT NULL,
            'country' TEXT NOT NULL,
            'Language' TEXT NOT NUll,
            'Director' TEXT NOT NULL,
            'Writer' TEXT NOT NULL, 
            'Production_Company' TEXT NOT NULL,
            'Actors' TEXT NOT NULL,
            'Description' TEXT NOT NULL,
            'AvgVote' INTEGER NOT NULL,
            'Votes' INTEGER NOT NULL,
            'Budget' REAL NOT NULL

        );

    '''
 

    cur.execute(drop_star)
    cur.execute(create_stars)
    cur.execute(drop_director)
    cur.execute(create_director)
    cur.execute(drop_movie)
    cur.execute(create_movie)
    cur.execute(drop_csv)
    cur.execute(create_additional_movies)
    cur.execute(drop_additional_ratings)
    cur.execute(create_additional_ratings)


    conn.commit()
    conn.close()

def insert_stuff_movies():
    conn = sqlite3.connect(DBNAME)
    conn.text_factory = str
    cur = conn.cursor()

    for film in movie_dict:

        insertion = (None, film, movie_dict[film]['ranking'], movie_dict[film]['year_published'], movie_dict[film]['average_rating'], movie_dict[film]['content_rating'])
        statement = 'INSERT INTO "Movies" '
        statement += 'VALUES (?, ?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)


    conn.commit()
    conn.close()

def create_star():
    conn = sqlite3.connect(DBNAME)
    conn.text_factory = str
    cur = conn.cursor()

    for star in movie_star:
        insertion = (None, star[0], star[1])  
        statement = 'INSERT INTO "Stars"' 
        statement += 'VALUES (?, ?, ?)' 
        cur.execute(statement, insertion)

    conn.commit()
    conn.close()


def create_director():
    conn = sqlite3.connect(DBNAME)
    conn.text_factory = str
    cur = conn.cursor()

    for director in movie_director:
        insertion = (None, director[0], director[1])  
        statement = 'INSERT INTO "Directors"' 
        statement += 'VALUES (?, ?, ?)' 
        cur.execute(statement, insertion)

    conn.commit()
    conn.close()  

def create_additional_movies():
    file_contents = open('IMDb_movies.csv', 'r')
    csv_reader = csv.reader(file_contents)
    conn = sqlite3.connect(DBNAME)
    #conn.text_factory = str 
    curr = conn.cursor()


    for row in csv_reader:

        insertion = (None, row[0], row[1], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16])
        statement = 'INSERT INTO "Additional_Movies"'
        statement += 'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        curr.execute(statement, insertion) 

    conn.commit()
    conn.close()


def create_additional_ratings():
    file_contents = open('IMDb_ratings.csv', 'r')
    csv_reader = csv.reader(file_contents)

    conn = sqlite3.connect(DBNAME) 
    #conn.text_factory = str 
    curr = conn.cursor()

    for row in csv_reader:

        insertion = (None, row[0], row[2], row[3], row[4], row[32], row[42])
        statement = 'INSERT INTO "Additional_Movies_Ratings"'
        statement += 'VALUES (?, ?, ?, ?, ?, ?, ?)'
        curr.execute(statement, insertion) 

    conn.commit()
    conn.close()

	

#Interactive Portion

def plot_year_count():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    look_up = '''

    SELECT Years, COUNT(*)
    FROM Additional_Movies
    GROUP BY Years 

    '''

    query = cur.execute(look_up)
    query = list(cur.fetchall())
    conn.commit()
    conn.close()

    Years = []
    count = []

    for i in query:
        Years.append(i[0])
        count.append(i[1])

    fig = go.Figure([go.Bar(x=Years, y=count, text=count, textposition='auto')])  
    fig.show()


def plot_rating_count():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    look_up = '''

        SELECT ContentRating, COUNT(*)
        FROM Movies
        GROUP BY ContentRating;


    '''

    query = cur.execute(look_up)
    query = list(cur.fetchall())
    conn.commit()
    conn.close()

    ratings = []
    count = []

    for i in query:
        ratings.append(i[0])
        count.append(i[1])

    fig = go.Figure([go.Bar(x=ratings, y=count, text=count, textposition='auto')])  
    fig.show()

def plot_average_count():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    look_up = '''

        SELECT AverageRating, COUNT(*)
        FROM Movies
        GROUP BY AverageRating;


    '''

    query = cur.execute(look_up)
    query = list(cur.fetchall())
    conn.commit()
    conn.close()

    ratings = []
    count = []

    for i in query:
        ratings.append(i[0])
        count.append(i[1])

    fig = go.Figure([go.Bar(x=ratings, y=count, text=count, textposition='auto')])  
    fig.show()
     
def plot_duration():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    look_up = '''

        SELECT duration, COUNT(*)
        FROM Additional_Movies
        GROUP BY duration
        HAVING duration < 300;


    '''

    query = cur.execute(look_up)
    query = list(cur.fetchall())
    conn.commit()
    conn.close()

    duration = []
    count = []

    for i in query:
        duration.append(i[0])
        count.append(i[1])

    fig = go.Figure([go.Bar(x=duration, y=count, text=count, textposition='auto')])  
    fig.show()

def table_movies():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    look_up = '''

        SELECT Ranking, Title
        FROM Movies; 


    '''

    query = cur.execute(look_up)
    query = list(cur.fetchall())
    conn.commit()
    conn.close()

    ranking = []
    title = []

    for i in query:
        ranking.append(i[0])
        title.append(i[1])

    fig = go.Figure(data = [go.Table(header = dict(values=['Movie Title', 'Ranking']), cells =dict(values=[[x for x in title], [x for x in ranking]])) 
    ])
    fig.show()

def plot_rating_content():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    look_up = '''

        SELECT AverageRating, Ranking
        FROM Movies;


    '''

    query = cur.execute(look_up)
    query = list(cur.fetchall())
    conn.commit()
    conn.close()

    AverageRating = []
    Rank = []

    for i in query:
        AverageRating.append(i[0])
        Rank.append(i[1])

    fig = go.Figure([go.Scatter(x=Rank, y=AverageRating)])  
    fig.show()

def director_count():
    conn = sqlite3.connect(DBNAME) 
    curr = conn.cursor()

    look_up = '''

        SELECT DirectorName, COUNT(*) as MovieNum
        FROM Directors LEFT JOIN Movies ON Directors.MovieName = Movies.Title
        GROUP BY DirectorName
        HAVING MovieNum > 1
        ORDER BY MovieNum DESC;

    '''

    query = curr.execute(look_up)
    query = list(curr.fetchall())

    director = []
    count = []
    for i in query:
        director.append(i[0])
        count.append(i[1])

    fig = go.Figure([go.Bar(x=director, y=count, text = count, textposition = 'auto')])
    fig.show()       
    

def actor_count():
    conn = sqlite3.connect(DBNAME) 
    curr = conn.cursor()

    look_up = '''

    SELECT ActorName, COUNT(*) as MovieNum
    FROM Stars LEFT JOIN Movies ON Stars.MovieName = Movies.Title
    GROUP BY ActorName
    HAVING MovieNum > 1
    ORDER BY MovieNum DESC; 

    '''

    query = curr.execute(look_up)
    query = list(curr.fetchall())

    conn.commit()
    conn.close()

    actor = []
    count = []
    
    for i in query:
        actor.append(i[0])
        count.append(i[1])

    fig = go.Figure([go.Bar(x=actor, y=count, text=count, textposition = 'auto')])
    fig.show()   



if __name__ == '__main__':
    #app.run(debug = True)
    CACHE_DICT = open_cache()
    init_db()
    create_star()
    create_director()
    insert_stuff_movies()
    create_additional_movies()
    create_additional_ratings()

    print('Welcome to the Movie Information Data House')
    print('')
    print('Here are your options for information')
    user1 = '''
    Option 1: See a table of the IMDb Top 250 Movies (Enter 1)
    Option 2: See a Graph of Number of Movies Per Year from an IMDb database (Enter 2) 
    Option 3: See a Graph of the Number of Movies Per Duration from an IMDb database (Enter 3)
    Option 4: See a Graph of Average Content from IMDb Top 250 Chart (Enter 4)
    Option 5: See a Graph of Avergae Ratings from IMDb Top 250 Chart (Enter 5)
    Option 6: See a Graph of the Rank and Average Rating from the IMDb Top 250 Chart (Enter 6)
    Option 7: See a Graph of the Top Count of Directors from the IMDb Top 250 Chart (Enter 7)
    Option 8: See a Graph of the Top Count of Stars from the IMDb Top 250 Chart (Enter 8)  
    Option 9: Exit the Data House (Enter 9)
    Option 10: Bring up the menu again (Enter 10) 
    '''

    print(user1)
    

    while True:
        user_input = input('Please select a number: ')
        if user_input == '1':
            print('Table of Top 250 Movies')
            print('May take a while to appear in webbrowser')
            table_movies()
        elif user_input == '2':
            print('Ploting Number of Movies per Year')
            print('May take a while to appear in webbrowser')
            plot_year_count()
        elif user_input == '3':
            print('Ploting Number of Movies per Duration')
            print('May take a while to appear in webbrowser')
            plot_duration()
        elif user_input == '4':
            print('Ploting Average Content Rating from Top 250')
            print('May take a while to appear in webbrowser')
            plot_rating_count()
        elif user_input == '5':
            print('Ploting Average Rating Score from Top 250')
            print('May take a while to appear in webbrowser')
            plot_average_count()
        elif user_input == '6':
            print('Ploting Graph of the Rank versus Average Rating')
            print('May take a while to appear in webbrowser')
            plot_rating_content()
        elif user_input == '7': 
            print('Ploting Graph of Top Director Count')
            print('May take a while to appear in webbrowser')
            director_count()
        elif user_input == '8':
            print('Ploting Graph of Top Actor Count')
            print('May take a while to appear in webbrowser')
            actor_count()       
        elif user_input == '9':
            break
        elif user_input == '10':
            print(user1)
        else:
            print('[Error] Not a Valid Input, please select number 1-10')     

    print('Now Exiting Application: Thank you for visiting the Movie Data House!')





