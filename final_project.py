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

DBNAME = 'movie_info.sqlite'

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

    create_movie = '''
        
        CREATE TABLE 'Movies' (
                'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
                'Title' TEXT NOT NULL,
                'Ranking' INTERGER,
                'Year' INTEGER,
                'AverageRating' REAL NOT NULL,
                'ContentRating' TEXT NOT NULL
        );
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

    create_additional_movies = '''

        CREATE TABLE 'Additional_Movies' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
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
    cur.execute(drop_movie)
    cur.execute(create_movie)
    cur.execute(drop_star)
    cur.execute(create_stars)
    cur.execute(drop_director)
    cur.execute(create_director)
    cur.execute(drop_csv)
    cur.execute(create_additional_movies)

    conn.commit()
    conn.close()

def insert_stuff_movies():
    conn = sqlite3.connect(DBNAME)
    conn.text_factory = str
    cur = conn.cursor()

    for film in movie_dict:

        insertion = (None, film,  movie_dict[film]['ranking'], movie_dict[film]['year_published'], movie_dict[film]['average_rating'], movie_dict[film]['content_rating'])
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
    file_contents = open('IMDB_movies.csv', 'r')
    csv_reader = csv.reader(file_contents)
    conn = sqlite3.connect(DBNAME) 
    conn.text_factory = str 
    curr = conn.cursor()

    for row in csv_reader:

        insertion = (None, row[1], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16])
        statement = 'INSERT INTO "Additional_Movies"'
        statement += 'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        curr.execute(statement, insertion) 

    conn.commit()
    conn.close()            
	

#Flask App Attempt

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

    
if __name__ == '__main__':
    #app.run(debug = True)
    CACHE_DICT = open_cache()
    init_db()
    insert_stuff_movies()
    create_star()
    create_director()
    create_additional_movies()

    print('Welcome to the Movie Information Data House')
    print('')
    print('Here are your options for information')
    user1 = '''
    Option 1: See a Graph of Number of Movies Per Year from an IMDb database (Enter 1) 
    Option 2: See a Graph of the Number of Movies Per Duration from an IMDb database (Enter 2)
    Option 3: See a Graph of Average Content from IMDb Top 250 Chart (Enter 3)
    Option 4: See a Graph of Avergae Ratings from IMDB Top 250 Chart (Enter 4)
    Option 5: Exit the Data House
    Option 6: Bring up the menu again 
    '''

    print(user1)
    

    while True:
        user_input = input('Please select a number: ')
        if user_input == '1':
            print('Ploting Number of Movies per Year')
            print('May take a while to appear in webbrowser')
            plot_rating_count()
        elif user_input == '2':
            print('Ploting Number of Movies per Duration')
            print('May take a while to appear in webbrowser')
            plot_duration()
        elif user_input == '3':
            print('Ploting Average Content Rating from Top 250')
            print('May take a while to appear in webbrowser')
            plot_rating_count()
        elif user_input == '4':
            print('Ploting Average Rating Score from Top 250')
            print('May take a while to appear in webbrowser')
            plot_average_count()
        elif user_input == '5':
            break
        elif user_input == '6':
            print(user1)
        else:
            print('[Error] Not a Valid Input, please select number 1-6')     

    print('Now Exiting Application: Thank you for visiting the Movie Data House!')





  

    

  
		

	
		
    

#print(film_dict[movie_name]['movie_name'])    



