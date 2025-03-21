import requests
from bs4 import BeautifulSoup

# Function to extract additional movie details from the Douban page
def extract_movie_details(movie_url, headers):
    movie_details = {"language": None, "length": None, "alt_titles": None, "imdb": None}
    
    response = requests.get(movie_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the div with id="info"
    info_div = soup.find('div', id='info')
    
    if info_div:
        # Language (found in the "语言" field)
        language = info_div.find("span", text="语言:")
        if language:
            movie_details["language"] = language.find_next("span").text.strip()

        # Length (found in the "片长" field)
        length = info_div.find("span", text="片长:")
        if length:
            movie_details["length"] = length.find_next("span").text.strip()

        # Alternative titles (found in the "又名" field)
        alt_titles = info_div.find("span", text="又名:")
        if alt_titles:
            movie_details["alt_titles"] = alt_titles.find_next("span").text.strip().split(" / ")

        # IMDb (found in the "IMDb" field)
        imdb = info_div.find("span", text="IMDb:")
        if imdb:
            imdb_link = imdb.find_next("a")
            if imdb_link:
                movie_details["imdb"] = imdb_link["href"]
            else:
                movie_details["imdb"] = None  # No IMDb link if not found
    
    return movie_details
