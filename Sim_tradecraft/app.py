# Main project file for TradeCraft
# Imports
import datetime
import sqlite3
from models import get_price, list_companies, COMPANIES
from flask import Flask, render_template, session, redirect, url_for, jsonify
from flask import request, flash
from werkzeug.security import generate_password_hash, check_password_hash
# Custom module to which is used to create the database
from create_db import create_db

net_worth = 0
# Database  functions for managing the users cash
def collect_user_cash(connection, user_identifier):
    return float(connection.execute('SELECT cash FROM users WHERE id=?', (user_identifier,)).fetchone()['cash'])


def _set_user_cash(connection, user_identifier, cash):
    connection.execute('UPDATE users SET cash=? WHERE id=?', (round(cash, 2), user_identifier))


create_db()

news_data = [
    {
        "title": "Netflix",
        "description": "Stocks : 0",
        "logo": "https://logo.clearbit.com/Netflix.com"
    },
    {
        "title": "Amazon",
        "description": "Amazon announces plans for AI to replace jobs CEO Andy Jassy said...",
        "logo": "https://logo.clearbit.com/amazon.com"
    },
    # Add more news here...
]

# Flask setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'


# ------------------- Routes ------------------- #

@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('news'))

    if request.method == 'POST':
        username = request.form['Username']  # fixed name
        password_input = request.form['password']

        with sqlite3.connect('tradecraft.db') as conn:
            cursor = conn.cursor()
            result = cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,)).fetchone()

        if result and check_password_hash(result[1], password_input):
            session['user_id'] = result[0]
            session['username'] = username
            flash("Login successful!", "success")
            return redirect(url_for('news'))
        else:
            flash("Invalid credentials", "error")
            return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            with sqlite3.connect('tradecraft.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users(username, password_hash) VALUES (?, ?)',
                    (username, generate_password_hash(password))
                )
                conn.commit()
                flash('Account created. You can now log in.', "success")
        except sqlite3.IntegrityError:
            flash('Username already exists.', "error")

        return redirect(url_for('login'))

    return render_template('signup_page.html')


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    return render_template('forgot_password.html')


# Trade route
@app.route('/trading', methods=['GET', 'POST'])
def trade():
    # Ensure user is logged in
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    # Handle form submission
    if request.method == 'POST':
        symbol = (request.form.get('symbol') or '').upper().strip()
        side = (request.form.get('side') or 'BUY').upper()
        try:
            # define cash as global variable
            qty = int(request.form.get('qty') or '0')
            with sqlite3.connect("tradecraft.db") as conn:
                conn.row_factory = sqlite3.Row  # lets you access columns by name
                cursor = conn.cursor()
                cursor.execute("SELECT cash FROM users WHERE id = ?", (session['user_id'],))
                result = cursor.fetchone()
                if result:
                    cash = result["cash"]
                print(cash)

                result = cursor.fetchone()
                if result:
                    cash = result["cash"]

            if qty <= 0:
                flash("Quantity must be positive.", "error")

            if cash == 0:
                flash("Insufficient funds to complete the purchase.", "error")

        except ValueError:
            # redirect to trade page
            return redirect(url_for('trade'))
        if symbol not in COMPANIES:
            return redirect(url_for('news'))
        price = get_price(symbol)
        total_price = price * qty
        try:
            # Connect to the database
            with sqlite3.connect('tradecraft.db') as conn:
                cursor = conn.cursor()
                local_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if side == 'BUY':
                    cash = cash - total_price
                else:
                    cash = cash + total_price
                cursor.execute(
                    'INSERT INTO transactions(user_id, symbol, qty, side, price, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
                    (session['user_id'], symbol, qty, side, total_price, local_time))
                conn.commit()
            with sqlite3.connect("tradecraft.db") as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET cash = ? WHERE id = ?", (cash, session['user_id'],))
                conn.commit()


        except Exception as e:
            print(str(e))
    # Update user's trade history balance
    with sqlite3.connect('tradecraft.db') as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM transactions WHERE user_id = ?", (session['user_id'],))

        transactions = cursor.fetchall()
        print(transactions)
    headings = ("ID", "User ID", "Symbol", "Quantity", "Side", "Price", "Timestamp")
    return render_template('trade.html', headings=headings, data=transactions)


@app.route('/Portfolio', methods=['GET'])
def portfolio():
    global net_worth
    # Ensure user is logged in
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
# Fetch transactions for the logged-in user
    with sqlite3.connect('tradecraft.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT symbol, qty, side FROM transactions WHERE user_id = ?", (session['user_id'],))
        rows = cursor.fetchall()
#   Calculate net holdings
    totals = {}
    for symbol, qty, side in rows:
        # Initialize if not present
        if side == 'BUY':
            totals[symbol] = totals.get(symbol, 0) + qty

        elif side == 'SELL':
            totals[symbol] = totals.get(symbol, 0) - qty

        company_data = [{"title": "Amazon.com, Inc.", "description": "", "logo": "https://logo.clearbit.com/amazon.com",
                         "symbol": "AMZN"},
                        {"title": "Netflix, Inc.", "description": "", "logo": "https://logo.clearbit.com/NETFLIX.com",
                         "symbol": "NFLX"}, {"title": "Chevron Corporation", "description": "",
                                             "logo": "https://logo.clearbit.com/chevron.com", "symbol": "CVX"},
                        {"title": "Exxon Mobil Corporation", "description": "",
                         "logo": "https://logo.clearbit.com/exxonmobil.com", "symbol": "XOM"},
                        {"title": "Pfizer Inc.", "description": "", "logo": "https://logo.clearbit.com/pfizer.com",
                         "symbol": "PFE"}, {"title": "Home Depot, Inc.", "description": "",
                                            "logo": "https://logo.clearbit.com/homedepot.com", "symbol": "HD"},
                        {"title": "Tootsie Roll Industries, Inc.", "description": "",
                         "logo": "https://logo.clearbit.com/tootsie.com", "symbol": "TR"},
                        {"title": "The Kraft Heinz Company", "description": "",
                         "logo": "https://logo.clearbit.com/kraftheinzcompany.com", "symbol": "KHC"},
                        {"title": "Johnson & Johnson", "description": "", "logo": "https://logo.clearbit.com/jnj.com",
                         "symbol": "JNJ"}, {"title": "General Motors Company", "description": "",
                                            "logo": "https://logo.clearbit.com/gm.com", "symbol": "GM"},
                        {"title": "Nike, Inc.", "description": "", "logo": "https://logo.clearbit.com/nike.com",
                         "symbol": "NKE"}, {"title": "The Walt Disney Company", "description": "",
                                            "logo": "https://logo.clearbit.com/disney.com", "symbol": "DIS"},
                        {"title": "Under Armour, Inc.", "description": "",
                         "logo": "https://logo.clearbit.com/underarmour.com", "symbol": "UAA"},
                        {"title": "Chipotle Mexican Grill, Inc.", "description": "",
                         "logo": "https://logo.clearbit.com/chipotle.com", "symbol": "CMG"},
                        {"title": "Starbucks Corp", "description": "",
                         "logo": "https://logo.clearbit.com/starbucks.com", "symbol": "SBUX"},
                        {"title": "McDonald's Corporation", "description": "",
                         "logo": "https://logo.clearbit.com/mcdonalds.com", "symbol": "MCD"},
                        {"title": "Ford Motor Company", "description": "", "logo": "https://logo.clearbit.com/ford.com",
                         "symbol": "F"},
                        {"title": "Tesla, Inc.", "description": "", "logo": "https://logo.clearbit.com/tesla.com",
                         "symbol": "TSLA"},
                        {"title": "Facebook, Inc.", "description": "", "logo": "https://logo.clearbit.com/meta.com",
                         "symbol": "META"}, {"title": "Rolls-Royce Holdings", "description": "",
                                             "logo": "https://logo.clearbit.com/rolls-royce.com", "symbol": "RR.L"},
                        {"title": "Samsung Electronics", "description": "",
                         "logo": "https://logo.clearbit.com/samsung.com", "symbol": "005930.KQ"},
                        {"title": "Apple Inc.", "description": "", "logo": "https://logo.clearbit.com/apple.com",
                         "symbol": "AAPL"}, {"title": "Microsoft Corporation", "description": "",
                                             "logo": "https://logo.clearbit.com/microsoft.com", "symbol": "MSFT"},
                        {"title": "NVIDIA Corporation", "description": "",
                         "logo": "https://logo.clearbit.com/nvidia.com", "symbol": "NVDA"},
                        {"title": "Google LLC", "description": "", "logo": "https://logo.clearbit.com/google.com",
                         "symbol": "GOOGL"}, {"title": "Comcast Corp (CMCSA)", "description": "",
                                              "logo": "https://logo.clearbit.com/comcast.com", "symbol": "CMCSAL"},
                        {"title": "Campbell's Soup", "description": "",
                         "logo": "https://logo.clearbit.com/campbells.com", "symbol": "CPB"},
                        {"title": "Walmart Inc.", "description": "", "logo": "https://logo.clearbit.com/walmart.com",
                         "symbol": "WMT"}
                        ]

    for item in company_data:
        symbol = item["symbol"]
        if symbol in totals and totals[symbol] > 0:
            item["description"] = f"{symbol} = {totals[symbol]} shares"
            net_worth = get_price(symbol) * totals[symbol] + net_worth
# Remove companies with empty descriptions
    company_data = [item for item in company_data if item["description"].strip() != ""]

    with sqlite3.connect("tradecraft.db") as conn:
        conn.row_factory = sqlite3.Row  # lets you access columns by name
        cursor = conn.cursor()
        cursor.execute("SELECT cash FROM users WHERE id = ?", (session['user_id'],))
        result = cursor.fetchone()
        if result:
            cash = result["cash"]
            # print(cash)
    total = cash + net_worth
    cash = "You have " + "£ " + str(cash) + " in your account" + " and your net worth is £" + str(total)
    return render_template("Portfolio.html", Stock=company_data, Portfolio_info=cash)


@app.route('/News')
def news():
    return render_template('News.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))


@app.get('/api/quote')
def api_quote():
    symbols = (request.args.get('symbols') or '').upper().replace(' ', '')
    out = {}
    for s in symbols.split(','):
        if not s:
            continue
        p = get_price(s)
        if p is not None:
            out[s] = {'symbol': s, 'price': p, 'ts': datetime.datetime.now(datetime.timezone.utc).isoformat() + 'Z'}
    return jsonify({'quotes': out})


@app.route('/research', methods=['GET', 'POST'])
def research():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    comps = list_companies()
    for c in comps:
        c['live_price'] = get_price(c['symbol'])
    return render_template('research.html', companies=comps)


@app.route('/rules')
def rules():
    return render_template('rules.html')


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
