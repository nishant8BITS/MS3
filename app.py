import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.secret_key = os.environ.get('SECRET_KEY')

mongo = PyMongo(app)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        # checks if name exists in database
        name_exists = mongo.db.user_logins.find_one(
            {'username': request.form.get('username').lower()})
 
        if name_exists:
            flash('User-Name already exists, please choose another name')
            return redirect (url_for('register'))

        register = {
            'username': request.form.get('username').lower(),
            'password': generate_password_hash(request.form.get('password'))
        }
        mongo.db.user_logins.insert_one(register)
        # puts new user into session
        session['user'] = request.form.get('username').lower() 
        flash('Registration was successful')
        return redirect(url_for('index', username=session['user']))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # checks if name exists
        name_exists = mongo.db.user_logins.find_one(
            {"username": request.form.get("username").lower()})

        if name_exists:
            # ensure hashed password matches user input
            if check_password_hash(
                name_exists["password"], request.form.get('password')):
                    session["user"] = request.form.get('username').lower()
                    flash('Welcome Again!')
                    return redirect(url_for('index', username=session['user']))
            else:
                # if invalid password
                flash('Incorrect Username and/or Password')
                return redirect(url_for("login"))

        else:
            # if name doesn't match
            flash('Incorrect Username and/or Password')
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route('/')
@app.route("/index", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route('/logout')
def logout():
    # removes session for user
    session.clear()
    flash("You're logged out")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
