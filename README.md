# Final Movie Project

Welcome to the world of movies at the Movie Data House! 

After interacting with this project, you will become a movie wizard and be ready for trivia night!

The files located in this respoitory will give you access to thousands of movies with great ratings from across decades.

This will provide the user with great information and statstics regarding thousands of movies in graphical representations in their webbrowser. 

The data from this project comes from scrapping the IMDb Top 250 Page and and IMDb database from Kaggle that provides movie information for over 90,000 movies.

# What you need to Download 
 - Download final_project.py
 - Head to the Master Branch of this project
   - Download Sqlite3 movie_information database 
   - Download both IMDb_ratings.csv and IMDb_movies.csv (if not downloaded from Kaggle already)

# Required Packages for running this code
 - Requests, csv
 - json
 - bs4, import Beautiful Soup
 - sqlite3
 - plotly.graph_objects as go

# Data Sources

IMDB website 
source: https://www.imdb.com/chart/top?ref_=nv_mv_250

Information from the top 250 chart was scrapped using the Beautiful Soup Package, this information incdludes topics such as movie name, ranking, directors, actors, year, average rating, and content rating. 

IMBD Movie Database
source: https://www.kaggle.com/stefanoleone992/imdb-extensive-dataset. 

IMDb movie database that houses the records of over 90,000 movies originating from the 1800s. This data is in a csv format and the movies and ratings files were used. 

# Database

An sqlite3 database was used to house this infomration for storage and retriveal for the ploty graphs. 

# Interaction and Presentation Options 

To interact with this project, download the final_project.py. After the file runs the user will be presented with 10 options for interaction in the command line. These graphs are generating from query the database that houses the source information. Using plotly, a table, scatter plot, and bar graph are used for this project, obtaining infomration from a query form the sqlite3 database. 

The user will see the menu on the different options and what will appear with each input. 

Here are the following user inputs that are options:
  - Option 1: See a table of teh IMDb Top 250 Movies (Enter 1)
  - Option 2: See a Graph of the Number of Movies per Year from an IMDb database (Enter 2)
  - Option 3: See a Graph of the Number fo Movies per Time Duration from an IMDb database (Enter 3)
  - Option 4: See a Graph of the Average Content Ratings from IMDb Top 250 Chart (Enter 4)
  - Option 5: See a Graph of the Average Ratings from IMDb Top 250 Chart (Enter 5)
  - Option 6: See a Graph of the Rank and Average Rating from the IMDb Top 250 Chart (Enter 6)
  - Option 7: See a Graph of the Top Count of Directors from the IMDb Top 250 Chart (Enter 7)
  - Option 8: See a Graph of the Top Count of Stars from the IMDb Top 250 Chart (Enter 8)
  - Option 9: Exit the Data House (Enter 9)
  - Option 10: Bring up the menu again (Enter 10)

The user will be prompted with the following question 
  - Please select a Number:

Once the user inputs, option 1-8 a graph will display in their webbrowser. If the user selects, option 9 they application will exit. If the user selects option 10, all options will display again. The user will be able to put in as many options in one application running as they please until they exit. The user input will also make sure only valid options numbers 1-10 are entered into the applications and interactive command line prompt. 

# I hope you enjoy this project!


