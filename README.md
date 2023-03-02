
# FIBER+

## Description:
Recipe Search App
This is a simple web app that allows users to search and bookmark recipes based on a list of ingredients. The app uses the Edamam Recipe Search API to search for recipes and display the results to the user.

## Features:

- User registration and login system
- Recipe search based on ingredients
- Display of recipe results including recipe name, ingredients, URL, and image
- Option to view more details about a specific recipe and the original site of the recipe.
## Technologies

- Flask
- Python
- SQLite
- Javascript
- HTML
- CSS
- Bootstrap 5

## Prerequisites
### To run this app, you will need the following software:

- Python 3
- Flask
- SQLite
### You will also need an API key and application ID from the Edamam Recipe Search API.

## Running the App

- Clone the repository to your local machine.

- Navigate to the project directory.

- Set the FLASK_APP environment variable.
 ->export FLASK_APP=app.py
- Set the APP_ID and APP_KEY variables inside config.ini with your API credentials.
- Run the app:
 -> flask run
- Open a web browser and go to http://localhost:5000 to access the app.


## Screenshots
## Login/Register
![Login](.\static\documentation_images\login.png)

![Register](.\static\documentation_images\register.png)

### Users have to create an account before using this application. Users have to 
### provide a username and a password, which will be stored in a database after the password
### is hashed. For safety measures, PLEASE DO NOT USE YOUR ACTUAL PASSWORD!

## Index
![Index](.\static\documentation_images\home.png)

### We greet the user with their username. User can fill the query with the ingredient/s of their liking (eg. Ingredients in their fridge) and
### search for recipes that match these ingredients.


## Result Page
![Results](.\static\documentation_images\search_results.png)

![Results](.\static\documentation_images\search_results_modal.png)

### Recipes that match users ingredients will be shown in this page as cards with some of the recipes info(image, title, dish type). A search bar above the cards can redirect user to a new search with another ingredients. 
### User can click on the card they want and a modal will show up with more information about the recipe like ingredients, health labels, total time, calories and a link to the original site of the recipe.
### They can also add the recipe to their bookmars by the button at the bottom of the modal.

## Bookmarks page

![Bookmarks](.\static\documentation_images\bookmarks.png)

![Bookmarks](.\static\documentation_images\bookmarks_modal.png)

### Very similar to results page but instead of the Bookmark button inside the modal, there is a Remove button so the user can delete the recipe from his bookmarks.

![Profile](.\static\documentation_images\profile.png)

### At the profile page users can change their current password. Validation is handled in back end. 

#### Credits to EDAMAM for providing the search API.