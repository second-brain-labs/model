from fastapi import FastAPI, HTTPException
import requests
import json

app = FastAPI()

EXTERNAL_SERVER_URL = "http://127.0.0.1:8000"

def get_user(url, name, email):
    user = {"name": name, "email": email}
    response = requests.post(f"{url}/users/login", json=user)
    if response.status_code < 300:
        print(f"User {name} created successfully!")
    else:
        print(f"{response.status_code} {response.reason} for user {name}")
    return response.json()

@app.get("/fetch-articles/{user_id}")
def fetch_articles(user):
    response = requests.get(f"{EXTERNAL_SERVER_URL}/articles/user/{user['uuid']}")
    return response.json()

# for testing
def make_some_entries_and_fetch():
    user1 = get_user(EXTERNAL_SERVER_URL, "John Doe", "johndoe@gmail.com")
    user2 = get_user(EXTERNAL_SERVER_URL, "Jane Doe", "janedoe@gmail.com")
    # print(requests.get(f"{EXTERNAL_SERVER_URL}/dummy/all/").json())
    print("articles for john: ", fetch_articles(user1))
    print("articles for jane: ", fetch_articles(user2))


# {'title': 'Title from populate_data.py', 
#  'user_uuid': 'de1cbfcb-dfb6-4165-8a15-93b8092f5fab', 
#  'directory': 'cs', 
#  'summary': 'Content from populate_data.py.', 
#  'id': 1, 
#  'time_created': '2023-11-25T22:12:44'}
def transform_json_input(input_json):
    # Extract values from input JSON
    title = input_json.get('title', '')
    directory = input_json.get('directory', '')
    summary = input_json.get('summary', '')
    article_id = input_json.get('id', '')
    time_created = input_json.get('time_created', '')

    # Construct the new JSON format
    transformed_json = {
        "fields": {
            "title": title,
            "content": summary,  # Assuming you want to use 'summary' as 'content'
            "abstract": summary,  # Assuming 'summary' also goes into 'abstract'
            "url": f"http://example.com/articles/{article_id}",  # Example URL, adjust as needed
            "directory": directory,
            "time_created": time_created
        }
    }

    return transformed_json


def transform_to_vespa():
    # dummy user 1 for now. TODO: change to be the actual user logged in
    user1 = get_user(EXTERNAL_SERVER_URL, "Jane Doe", "janedoe@gmail.com")
    articles = fetch_articles(user1)

    # Transform the input JSON
    new_json = [transform_json_input(article) for article in articles]
    return new_json

# for testing
def write_to_json_file(json_list, filename="data.json"):
    with open(filename, "w") as f:
        for entry in json_list:
            # Convert the JSON object to a string and write it to the file
            json_string = json.dumps(entry)
            f.write(json_string + '\n')

def feed_document_to_vespa(document, document_id, vespa_url='http://localhost:8080'):
    # Constructing the document API URL
    feed_url = f"{vespa_url}/document/v1/articles/articles/docid/{document_id}"

    # Headers for the request
    headers = {
        'Content-Type': 'application/json'
    }

    # Sending the POST request to Vespa
    response = requests.post(feed_url, headers=headers, data=json.dumps(document))

    # Check if the request was successful
    if response.status_code in [200, 201]:
        return response.json()
    else:
        raise Exception(f"Feeding failed with status code {response.status_code}: {response.text}")

def update_vespa_db():
    # dummy user 1 for now. TODO: change to be the actual user logged in
    user1 = get_user(EXTERNAL_SERVER_URL, "Jane Doe", "janedoe@gmail.com")
    articles = fetch_articles(user1)
    for article in articles:
        # Transform the input JSON
        new_json = transform_json_input(article)
        # Feed the document to Vespa
        document_id = f"{article['id']}"
        response = feed_document_to_vespa(new_json, document_id)
        print(response)

if __name__ == "__main__":
    json_list = transform_to_vespa()
    write_to_json_file(json_list)

    update_vespa_db()