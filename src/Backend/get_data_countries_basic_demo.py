import pandas as pd
import wikipediaapi
from tqdm import tqdm
import requests

# Function to fetch Wikipedia summary and detailed content for a given country
def fetch_wikipedia_data(country, wiki, session):
    page = wiki.page(country)

    data = {"country": country}
    
    if page.exists():
        data.update({
            "title": page.title,
            "summary": page.summary,
            "url": page.fullurl,
            "detailed_content": " ".join(page.text.split()[:2000])  # First 6000 words
        })
        
        # Fetch the last edited timestamp using MediaWiki API
        revisions_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=timestamp&titles={country}&format=json"
        revisions_response = session.get(revisions_url)
        
        if revisions_response.status_code == 200:
            revisions_data = revisions_response.json()
            page_id = next(iter(revisions_data['query']['pages']))
            if 'revisions' in revisions_data['query']['pages'][page_id]:
                last_edited = revisions_data['query']['pages'][page_id]['revisions'][0]['timestamp']
                data["last_edited"] = last_edited
            else:
                data["last_edited"] = ''
        else:
            data["last_edited"] = ''
            print(f"Failed to fetch last edited timestamp for {country}: {revisions_response.status_code}")

    else:
        print(f"Page does not exist for {country}")

    # Ensure all keys exist in the returned dictionary
    for key in ["title", "summary", "url", "last_edited", "detailed_content"]:
        data.setdefault(key, "")

    return data

# Read the CSV file with country information
csv_file_path = 'world-data-2023.csv'  # Replace with your CSV file path
df = pd.read_csv(csv_file_path)

# Initialize lists to store the Wikipedia data
titles = []
summaries = []
urls = []
last_edited = []
detailed_contents = []

# Initialize Wikipedia API and requests session
wiki = wikipediaapi.Wikipedia('globe_proj (samir.c.asghar@gmail.com)', 'en')
session = requests.Session()

# Fetch Wikipedia summaries for each country
for country in tqdm(df['Country']):  # Assuming the CSV has a column named 'Country'
    wiki_data = fetch_wikipedia_data(country, wiki, session)
    titles.append(wiki_data['title'])
    summaries.append(wiki_data['summary'])
    urls.append(wiki_data['url'])
    last_edited.append(wiki_data['last_edited'])
    detailed_contents.append(wiki_data.get('detailed_content', ''))

# Add the Wikipedia data to the DataFrame
df['wiki_title'] = titles
df['wiki_summary'] = summaries
df['wiki_url'] = urls
df['wiki_last_edited'] = last_edited
df['wiki_detailed_content'] = detailed_contents

# Save the combined data as a JSON file
json_file_path = 'countries_with_wikipedia13.json'  # Replace with your desired JSON file path
df.to_json(json_file_path, orient='records', indent=4)

print("Data fetching and saving completed successfully.")