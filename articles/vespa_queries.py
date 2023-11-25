import requests
import json

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

# Example query 1
query = 'select * from articles where default contains "dogs"'
response = run_vespa_query(query)
print(json.dumps(response, indent=2))

print('------------------------------------------')
# Example query 2
query = 'select * from articles where default contains "Messi"'
response = run_vespa_query(query)
print(json.dumps(response, indent=2))

print('------------------------------------------')
# Example query 3
query = 'select time_created from articles where default contains phrase("React","Typescript") order by time_created'
response = run_vespa_query(query)
print(json.dumps(response, indent=2))