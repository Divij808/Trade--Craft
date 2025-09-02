# test_db.py
import unittest
import sqlite3
from create_db import create_db, create_db_connection

class TestDatabaseSetup(unittest.TestCase):

    def setUp(self):
        # Keep the same in-memory DB connection alive
        self.conn = sqlite3.connect(":memory:")
        create_db_connection(self.conn)  # modified helper
        self.cursor = self.conn.cursor()

    def tearDown(self):
        self.conn.close()
    def test_users_table_exists(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        table = self.cursor.fetchone()
        self.assertIsNotNone(table, "Users table should exist")

    def test_transactions_table_exists(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions';")
        table = self.cursor.fetchone()
        self.assertIsNotNone(table, "Transactions table should exist")

    def test_users_table_schema(self):
        self.cursor.execute("PRAGMA table_info(users);")
        columns = {col[1] for col in self.cursor.fetchall()}
        expected = {"id", "username", "password_hash", "cash"}
        self.assertEqual(columns, expected)

    def test_transactions_table_schema(self):
        self.cursor.execute("PRAGMA table_info(transactions);")
        columns = {col[1] for col in self.cursor.fetchall()}
        expected = {"id", "user_id", "symbol", "qty", "side", "price", "timestamp"}
        self.assertEqual(columns, expected)


