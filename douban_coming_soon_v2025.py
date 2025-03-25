#how to: first run py server.py
#then run py douban_coming_soon_v2025.py
#then open upcoming_movies_douban.html

#to do (before putting on github)
#add a history
#add a compare function for any two dates
#add some error handling?

#to do (on github)
#run once per day (try midday)
#display webpage

#to do (after github?)
#get info from douban pages (info more reliable? plus there's more e.g. language, original title) -> then add a tab for language
#add login info so won't be blocked

import os
import requests
import pandas as pd
import re
from datetime import datetime
import io
from date_utils import convert_date
from bs4 import BeautifulSoup
import json
import logging

# Set Pandas options to display full table
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

logging.basicConfig(
    filename='scraping.log',  # Log output file
    level=logging.INFO,  # Set the logging level to INFO (or DEBUG for more details)
    format='%(asctime)s - %(levelname)s - %(message)s'
)

headers = {
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
}

url = 'https://movie.douban.com/coming'
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    logging.info(f"Successfully fetched the page: {url}")
else:
    logging.error(f"Failed to fetch the page: {url}, status code: {response.status_code}")

soup = BeautifulSoup(response.text, 'html.parser')

# Extract the first table using BeautifulSoup
table = soup.find('table')

# Log whether the table was found
if table:
    rows = table.find_all('tr')
    logging.info(f"Found the table with {len(rows)} rows.")
else:
    logging.error("Error: Table not found!")
    rows = []

data = []
for row in rows[1:]:  # Skip header row
    cols = row.find_all('td')
    release_date = cols[0].text.strip()
    title = cols[1].find('a').text.strip()
    genre = cols[2].text.strip()
    region = cols[3].text.strip()
    want_to_see = cols[4].text.strip()
    movie_url = cols[1].find('a')['href']

    data.append({
        'release_date': release_date,
        'title': title,
        'genre': genre,
        'region': region,
        'want_to_see': want_to_see,
        'url': movie_url
    })

df = pd.DataFrame(data)

# Convert "release_date" to YYYY-MM-DD format
df["release_date"] = df["release_date"].apply(convert_date)

# Split genre and region into lists
df["genre"] = df["genre"].apply(lambda x: x.split(" / ") if isinstance(x, str) else [])
df["region"] = df["region"].apply(lambda x: x.split(" / ") if isinstance(x, str) else [])

# Extract just the number from "want_to_see"
df["want_to_see"] = df["want_to_see"].apply(lambda x: int(re.sub(r"\D", "", str(x))) if isinstance(x, str) else 0)

# **Save Data for Comparison**
today = datetime.now().strftime('%Y-%m-%d')
os.makedirs(os.path.join("data"), exist_ok=True)  # Ensure the 'data' directory exists
csv_filename = os.path.join("data", f"movies_{today}.csv")  # Use os.path.join() for paths
df.to_csv(csv_filename, index=False, encoding='utf-8-sig')

print(f"Data saved to {csv_filename}")

# Load today's movie data
today_file = os.path.join("data", f"movies_{today}.csv")
df_today = pd.read_csv(today_file, encoding='utf-8-sig')



# Load yesterday’s data (if available)
yesterday = (datetime.now().replace(hour=0, minute=0, second=0) - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
yesterday_file = os.path.join("data", f"movies_{yesterday}.csv")

if os.path.exists(yesterday_file):
    df_prev = pd.read_csv(yesterday_file, encoding='utf-8-sig')
    print(f"Loaded previous day's data: {yesterday_file}")
else:
    df_prev = pd.DataFrame(columns=df_today.columns)  # Empty DataFrame if no previous data
    print("No previous day's data found.")

# **Compare using Douban URL as the key**
urls_today = set(df_today["url"])
urls_prev = set(df_prev["url"])

# Find **New Movies** (URLs in today’s list but not in yesterday’s)
new_movies = df_today[df_today["url"].isin(urls_today - urls_prev)]

# Find **Removed Movies** (URLs in yesterday’s list but missing today)
removed_movies = df_prev[df_prev["url"].isin(urls_prev - urls_today)].copy()

# Initialize old_release_date to the same value as release_date for all movies
df_today["old_release_date"] = df_today["release_date"]

# Merge today and previous data to find updated movies
print(f"df_today shape: {df_today.shape}")  # This will show the number of rows and columns in df_today
print(f"removed_movies shape: {removed_movies.shape}")  # This will show the number of rows and columns in removed_movies
updated_movies = df_today.merge(df_prev, on="url", suffixes=("_today", "_prev"))

# Set the old release date to the previous release date for updated movies where the release date has changed
df_today.loc[df_today["url"].isin(updated_movies[updated_movies["release_date_today"] != updated_movies["release_date_prev"]]["url"]), "old_release_date"] = updated_movies["release_date_prev"]

# Now, filter to get only updated movies where the release date has actually changed
updated_movies = updated_movies[updated_movies["release_date_today"] != updated_movies["release_date_prev"]]


# ✅ Distinguish between "Probably Dropped" and "Probably Released"
today_date = datetime.now().strftime('%Y-%m-%d')
removed_movies["status"] = removed_movies["release_date"].apply(
    lambda date: "Probably Released" if date == today_date else "Probably Dropped"
)

# ✅ Assign statuses to today's movies
df_today["status"] = "Upcoming"  # Default status
df_today.loc[df_today["url"].isin(new_movies["url"]), "status"] = "New"
df_today.loc[df_today["url"].isin(updated_movies["url"]), "status"] = "Updated"

# Print summary
print(f"\nNew Movies: {len(new_movies)}")
print(f"Probably Dropped Movies: {len(removed_movies[removed_movies['status'] == 'Probably Dropped'])}")
print(f"Probably Released Movies: {len(removed_movies[removed_movies['status'] == 'Probably Released'])}")
print(f"Updated Movies: {len(updated_movies)}")

# ✅ Save CSV results for all categories
#new_movies.to_csv(f"data/new_movies_{today}.csv", index=False, encoding="utf-8-sig")
#removed_movies.to_csv(f"data/removed_movies_{today}.csv", index=False, encoding="utf-8-sig")
#updated_movies.to_csv(f"data/updated_movies_{today}.csv", index=False, encoding="utf-8-sig")

print("\nComparison complete. Results saved.")

# ✅ Combine today’s and removed movies into a single dataset for JSON
df_combined = pd.concat([df_today, removed_movies], ignore_index=True)
df_combined["old_release_date"].fillna(df_combined["release_date"], inplace=True)
print(df_combined.head())
# Function to format release date and log invalid data
def format_release_date(date):
    # Check if the date is a valid string before applying replace
    if isinstance(date, str):
        return date.replace('-99', '-??')
    else:
        # Log the invalid (non-string) value
        print(f"Invalid value for release_date: {date}")  # Log this to GitHub Actions logs
        return date  # Return the value unchanged or as NaN if you prefer


df_combined["release_date"] = df_combined["release_date"].apply(format_release_date)
print(df_combined.head())  # This will show a few rows of the DataFrame to inspect the content.
print(df_combined["old_release_date"])
#df_combined["old_release_date"] = df_combined["old_release_date"].astype(str)
#df_combined["old_release_date"] = df_combined["old_release_date"].apply(lambda x: x.replace('-99', '-??') if isinstance(x, str) else x)

#df_combined["old_release_date"] = df_combined["old_release_date"].apply(format_release_date)

# ✅ Convert DataFrame to a list of dictionaries
movies_list = df_combined.to_dict(orient="records")

# ✅ Save the final JSON file
json_filename = f"data/movies_{today}.json"
with open(json_filename, "w", encoding="utf-8") as json_file:
    json.dump(movies_list, json_file, ensure_ascii=False, indent=4)

print(f"Movie data saved to {json_filename}")
