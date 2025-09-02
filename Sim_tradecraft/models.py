import datetime
import json
import math
import os
import random
import time

base_directory = os.path.dirname(os.path.abspath(__file__))

# Load company data from JSON file
with open(os.path.join(base_directory, 'data', 'companies.json'), 'r') as f:
    COMPANIES = {c['symbol']: c for c in json.load(f)}
    print(COMPANIES)


def collect_user_cash(connection, user_identifier):
    return float(connection.execute('SELECT cash FROM users WHERE id=?', (user_identifier,)).fetchone()['cash'])


# Helper function to set user cash
def _set_user_cash(connection, user_identifier, cash):
    connection.execute('UPDATE users SET cash=? WHERE id=?', (round(cash, 2), user_identifier))
    with open(os.path.join(base_directory, 'data', 'companies.json'), 'r') as f:
        COMPANIES = {c['symbol']: c for c in json.load(f)}
        print(COMPANIES)


# Stock market related utilities
def get_price(symbol: str) -> float:
    """Generate pseudo-random live stock price"""
    symbol = (symbol or '').upper().strip()
    if symbol not in COMPANIES:
        return None

    base_price = float(COMPANIES[symbol]['base_price'])
    minute_bucketed = int(time.time() // 60)
    seed_str = f"{symbol}:{minute_bucketed}"
    random1 = random.Random(seed_str)
    shocks = random1.uniform(-0.025, 0.025)

    day_within_the_year = int(datetime.datetime.utcnow().strftime('%j'))
    drift = 0.02 * math.sin((day_within_the_year / 365) * 2 * math.pi)
    cost = max(1.0, base_price * (1 + drift + shocks))
    return round(cost, 2)


def list_companies():
    """Helper: return list of all companies"""
    return list(COMPANIES.values())
