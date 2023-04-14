import psycopg2, psycopg2.extras
import requests
import configparser
from flask import Flask, redirect, render_template, request, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from helpers import login_required, apology


# Configure application
app = Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create a configparser object and read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Get the app_id and app_key values from the configuration file
app_id = config['DEFAULT']['app_id']
app_key = config['DEFAULT']['app_key']


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def recipe_search(param):
    url = f'https://api.edamam.com/api/recipes/v2?type=public&q={param}&app_id={app_id}&app_key={app_key}'
    result = requests.get(url)

    if result.status_code != 200:
        print(f'Error: {result.status_code} - {result.reason}')
        return None

    data = result.json()
    return data['hits']
    


@app.route("/")
@login_required
def index():
    """ Homepage """
    user_id = session["user_id"]
    # con = sqlite3.connect("Users.db")
    con = psycopg2.connect("postgres://nwobalvgtjvblb:6500a8e0f7c23222d2c5c783298a857170f1531b07c6e71536eb7aeeba726ee0@ec2-54-211-177-159.compute-1.amazonaws.com:5432/d1v5gbplsiu69j")
    con.row_factory = psycopg2.extras.DictCursor
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    rows = cur.fetchone()
    username = rows["username"]
    con.close()
    return render_template("index.html", username=username)


@app.route("/result")
@login_required
def results():
    
    # Get input values from user
    ingredients = request.args.getlist("ingredients")
    
    # Search for recipes from User's ingredients liking
    recipes = recipe_search(ingredients)
    # Create a new list
    list = []
    # Counter for the results counter
    count = 0
    # Iterate the results and asign to variables
    for result in recipes:
        link = result["_links"]["self"]["href"]
        label = result["recipe"]["label"]
        ingredientsL = result["recipe"]["ingredientLines"]
        url = result["recipe"]["url"]
        image = result["recipe"]["image"]
        calories = result["recipe"]["calories"]
        cuisineType = result["recipe"]["cuisineType"]
        # Check if the dishType key exists in the dictionary
        if "dishType" in result["recipe"]:
            # Get the dishType value from the dictionary
            dishType = result["recipe"]["dishType"]
        else:
            # Set the dishType value to an empty string if the key does not exist
            dishType = ""
        dishType = str(dishType).strip("['\',]")
        source = result["recipe"]["source"]
        dietLabels = result["recipe"]["dietLabels"]
        totalTime = result["recipe"]["totalTime"]
        mealType = result["recipe"]["mealType"]
        healthLabels = result["recipe"]["healthLabels"]

    # Append in list
        list.append({
            "link": link,
            "source": source,
            "label": label,
            "ingredients": ingredientsL,
            "url": url,
            "image": image,
            "calories": calories,
            "cuisineType": cuisineType,
            "dishType": dishType,
            "dietLabels": dietLabels,
            "totalTime": totalTime,
            "healthLabels": healthLabels,
            "mealType": mealType
        })
        count = count + 1

    con = psycopg2.connect("postgres://nwobalvgtjvblb:6500a8e0f7c23222d2c5c783298a857170f1531b07c6e71536eb7aeeba726ee0@ec2-54-211-177-159.compute-1.amazonaws.com:5432/d1v5gbplsiu69j")
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT link FROM bookmarks WHERE user_id = %s", [session["user_id"]])
    saved_recipes = cur.fetchall()
    con.close()
    return render_template("result.html", recipes=recipes, list=list, ingredients=ingredients, count=count, saved_recipes=saved_recipes)

@app.route("/register", methods=["GET", "POST"])
def register():
    # Register
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")
        # Ensure username was submitted
        if not username:
            return apology("Must provide username", 400)
        # Ensure password was submitted
        elif not password:
            return apology("Must provide password", 400)
        # Ensure password was submitted
        elif not confirm:
            return apology("Must provide  confirmation password", 400)
        if password != confirm:
            return apology("Must provide  the same password", 400)

        # Hash password
        hash = generate_password_hash(password)

        # Insert info in our table users
        try:
            con = psycopg2.connect("postgres://nwobalvgtjvblb:6500a8e0f7c23222d2c5c783298a857170f1531b07c6e71536eb7aeeba726ee0@ec2-54-211-177-159.compute-1.amazonaws.com:5432/d1v5gbplsiu69j")
            cur = con.cursor()
            query = "INSERT INTO users (username, hash) VALUES (%s, %s)"
            cur.execute(query, (username, hash))
            con.commit()
            con.close()
            return redirect("/")
        except psycopg2.IntegrityError:
            return apology("This Username already exists")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user In"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not password:
            return apology("Must provide password", 403)

        # Query database for username

        con = psycopg2.connect("postgres://nwobalvgtjvblb:6500a8e0f7c23222d2c5c783298a857170f1531b07c6e71536eb7aeeba726ee0@ec2-54-211-177-159.compute-1.amazonaws.com:5432/d1v5gbplsiu69j")
        cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        # Error handle if user doesn't exist
        try:
            rows = cur.fetchone()
        except:
            return apology("This Username doesn't exist")

        hash1 = rows["hash"]

        # Ensure username exists and password is correct
        if len([rows]) != 1 or not check_password_hash(hash1, password):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows['user_id']

        # Redirect user to home page
        con.close()

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/add", methods=["POST"])
@login_required
def add():
    """Add to database the recipes information that the user wants to bookmark"""
    # Get recipes data/ibfo that the user wants to bookmark
    link = request.form.get("link")
    label = request.form.get("label")
    image = request.form.get("image")
    source = request.form.get("source")
    url = request.form.get("url")
    calories = request.form.get("calories")
    mealType = request.form.get("mealType")
    totalTime = request.form.get("totalTime")

    dishType = request.form.get("dishType").strip("[]").strip(",")
    dietLabels = request.form.get("dietLabels").strip("[]").strip(",")
    healthLabels = request.form.get("healthLabels").strip("[]").strip(",")
    cuisineType = request.form.get("cuisineType").strip("[]").strip(",")
    ingredients = request.form.get("ingredients").strip("[]")

    # Connect to Users database
    con = psycopg2.connect("postgres://nwobalvgtjvblb:6500a8e0f7c23222d2c5c783298a857170f1531b07c6e71536eb7aeeba726ee0@ec2-54-211-177-159.compute-1.amazonaws.com:5432/d1v5gbplsiu69j")
    cur = con.cursor()
    # Insert into bookmarks in Users.db the data we got from the form for each recipe the user wants to bookmark
    cur.execute("INSERT INTO bookmarks (user_id, link, label, image, source, url, calories, meal_type, total_time, dish_type, diet_labels, health_labels, cuisine_type, ingredients) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (session["user_id"], link, label, image, source, url, calories, mealType, totalTime, dishType, dietLabels, healthLabels, cuisineType, ingredients))
    con.commit()
    con.close()

    # Redirect user to bookmarks
    return redirect("/bookmarks")


@app.route("/bookmarks")
@login_required
def bookmark():
    
    con = psycopg2.connect(
    "postgres://nwobalvgtjvblb:6500a8e0f7c23222d2c5c783298a857170f1531b07c6e71536eb7aeeba726ee0@ec2-54-211-177-159.compute-1.amazonaws.com:5432/d1v5gbplsiu69j"
    )
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
    "SELECT link FROM bookmarks WHERE user_id = %s",
    (session["user_id"],))
    saved_recipes = cur.fetchall()
    con.close()
    return render_template("bookmarks.html", saved_recipes=saved_recipes)


@app.route("/remove", methods=["POST"])
@login_required
def remove():
    link = request.form.get("link")

    con = psycopg2.connect("postgres://nwobalvgtjvblb:6500a8e0f7c23222d2c5c783298a857170f1531b07c6e71536eb7aeeba726ee0@ec2-54-211-177-159.compute-1.amazonaws.com:5432/d1v5gbplsiu69j")
    cur = con.cursor()
    cur.execute("DELETE FROM bookmarks WHERE link = %s", (link,))
    con.commit()
    con.close()

    return redirect("/bookmarks")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":

        # Query the database for the user id
        con = psycopg2.connect("postgres://nwobalvgtjvblb:6500a8e0f7c23222d2c5c783298a857170f1531b07c6e71536eb7aeeba726ee0@ec2-54-211-177-159.compute-1.amazonaws.com:5432/d1v5gbplsiu69j")
        cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT hash FROM users WHERE user_id = %s", (session["user_id"],))
        hashOld = cur.fetchone()[0]
        con.close()

        # Get the current password and the new password from the form
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        new_confirm_password = request.form.get("new_confirm_password")

      # Check for inputs
        if not current_password or not new_password or not new_confirm_password:
            return apology("You must fill in all fields", 403)

        # Check if new password and confirmations password match
        if new_password != new_confirm_password:
            return apology("New password and confirmation password must match", 403)

        # Ensure password is correct
        if not check_password_hash(hashOld, current_password):
            return apology("Current password is incorrect", 403)

        # Check if user entered the same password
        if current_password == new_password:
            return apology("New password can't be the same as the old password", 403)

        # Hash the new password and update the user's password in the database
        hashNew = generate_password_hash(new_password)
        con = psycopg2.connect("postgres://nwobalvgtjvblb:6500a8e0f7c23222d2c5c783298a857170f1531b07c6e71536eb7aeeba726ee0@ec2-54-211-177-159.compute-1.amazonaws.com:5432/d1v5gbplsiu69j")
        cur = con.cursor()
        cur.execute("UPDATE users SET hash = %s WHERE user_id = %s", (hashNew, session["user_id"]))
        con.commit()
        con.close()

        # Redirect to the home page
        flash("Password changed successfully!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("profile.html")


@app. errorhandler(404) 
def page_not_found(e): 
    return apology("Invalid route")

if __name__ == "__main__":
    app.run(debug=True)