import requests
import json

# TODO: find a better way to ensure that uuid is sent with query in integration
def run_vespa_query(query, vespa_url='http://localhost:8080'):
    # Constructing the Vespa YQL query URL
    query_url = f"{vespa_url}/search/"

    # Parameters for the query
    params = {
        'yql': query,
        'format': 'json'
    }

    # Sending the GET request to Vespa
    response = requests.get(query_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed with status code {response.status_code}: {response.text}")
    
def parse_vespa_query(response):
    if response["root"]["fields"]["totalCount"] > 0:
        return [{"title": child["fields"]["title"], "url": child["fields"]["url"]} for child in response["root"]["children"]]
    else:
        return "No articles matched your search."

example_queries = [
    'select * from articles where default contains "dogs"',
    'select * from articles where default contains "Messi"',
    'select time_created from articles where default contains phrase("React","Typescript") order by time_created'
]

for query in example_queries:
    response = run_vespa_query(query)
    print(json.dumps(response, indent=2))
    print(parse_vespa_query(response))
    print('------------------------------------------')