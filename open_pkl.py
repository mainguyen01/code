# import pickle

# with open('E:\web-scraping\guide_webscraping\quotes_js.pkl', 'rb') as f:
#     data = pickle.load(f)

# print(data)

import sqlite3

conn = sqlite3.connect("books.db")
cursor = conn.cursor()
cursor.execute("SELECT title,price FROM books")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()