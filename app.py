import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    list = db.execute("SELECT * FROM stock WHERE id = ?", session["user_id"])
    listuser = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    cashdict = listuser[0]
    Cash = round(cashdict['cash'], 2)
    return render_template("index.html", stocks=list, Cash=Cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = (request.form.get("symbol")).upper()
        stock = lookup(symbol)
        if stock == None:
            return apology("No stock found")
        shares = request.form.get("shares")
        try:
            shares = int(shares)
        except ValueError:
            return apology("not a number cuh", 400)
        if shares < 1:
            return apology("bruh", 400)
        shares = float(shares)
        price = float(stock['price'])
        row = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        dict = row[0]
        cash = dict['cash']
        total = price * shares
        if (cash < total):
            return apology("your broke", 400)
        newcash = cash - total
        list = db.execute("SELECT * FROM stock WHERE id = ? AND name = ?", session["user_id"], symbol)
        is_empty = True
        for _ in list:
            is_empty = False
            break  # Exit the loop as soon as one row is encountered
        if is_empty:
             db.execute("INSERT INTO stock (id, name, price, shares) VALUES (?, ?, ? ,?)", session["user_id"], symbol, price, shares)
        else:
            rowshare = db.execute("SELECT * FROM stock WHERE id = ? AND name = ?", session["user_id"], symbol)
            dictshare = rowshare[0]
            newshare = dictshare['shares'] + shares
            db.execute("UPDATE stock SET shares = ? WHERE id = ?", newshare, session['user_id'])
        db.execute("UPDATE users SET cash = ? WHERE id = ?", newcash, session['user_id'])
        return redirect("/")
    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    return render_template("history.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        stock = lookup(symbol)
        if stock == None:
            return apology("Not found")
        return render_template("quoted.html", name=stock['name'], symbol=stock['symbol'], price=stock['price'])
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # checking if the user actually put anything in the field
        if not request.form.get("username"):
            return apology("must provide username", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # check if confirmation is correct and name is available
        if (request.form.get("confirmation") != request.form.get("password")):
            return apology("wrong confirmation bro", 400)
        checkusername = request.form.get("username")
        result = db.execute("SELECT username FROM users WHERE username = ?", (checkusername,))
        if result:
            for dict in result:
                name = dict['username']
                if name == checkusername:
                    return apology("username taken bro", 400)
        checkpassword = generate_password_hash(request.form.get("password"))
        checkcash = 10000.00

        # if every condition pass, insert their data into the table.
        newid = 0
        iffirstperson = db.execute("SELECT MAX(id) FROM users")
        dict = iffirstperson[0]
        if dict['MAX(id)'] != None:
            newid = (dict['MAX(id)']) + 1
            db.execute("INSERT INTO users (id, username, hash, cash) VALUES (?, ?, ?, ?)", newid, checkusername, checkpassword, checkcash)
        elif dict['MAX(id)'] == None:
            db.execute("INSERT INTO users (id, username, hash, cash) VALUES (?, ?, ?, ?)", newid, checkusername, checkpassword, checkcash)

        session["user_id"] = newid
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    list = db.execute("SELECT * FROM stock WHERE id = ?", session["user_id"])

    listuser = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    dictuser = listuser[0]
    usercash = float(dictuser['cash'])

    if request.method == "POST":
        defaultstockpricedict = lookup(request.form.get("symbol"))
        defaultstockprice = defaultstockpricedict['price']
        stocklist = db.execute("SELECT * FROM stock WHERE id = ? AND name = ?", session["user_id"], request.form.get("symbol"))
        stockdict = stocklist[0]
        stockshare = float(stockdict['shares'])
        stockprice = float(stockdict['price'])
        wantsellshare = float(request.form.get("shares"))
        if (wantsellshare > stockshare):
            return apology("your overselling dawg")
        if stockshare == wantsellshare:
            db.execute("DELETE FROM stock WHERE id = ? AND name = ?", session["user_id"], request.form.get("symbol"))
        elif stockshare > wantsellshare:
            db.execute("UPDATE stock SET shares = ? WHERE id = ?", stockshare - wantsellshare, session['user_id'])
        db.execute("UPDATE users SET cash = ? WHERE id = ?", usercash + (wantsellshare * defaultstockprice), session['user_id'])
        return redirect("/")
    else:
        return render_template("sell.html", stocks=list)
