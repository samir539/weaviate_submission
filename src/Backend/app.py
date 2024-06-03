from flask import Flask, request, jsonify
import weaviate
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)


# Weaviate client setup
cluster_url = os.getenv("WEAVIATE_CLUSTER_URL")
auth_api_key = os.getenv("WEAVIATE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

client = weaviate.Client(
    url=cluster_url,
    auth_client_secret=weaviate.AuthApiKey(api_key=auth_api_key),
    additional_headers={
        "X-OpenAI-Api-Key": openai_api_key
    }
)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query')
    num_results = int(data.get('num_results', 10))

    if not query:
        return jsonify({"error": "No query provided"}), 400

    response = client.query \
        .get("DetailedCountry22", ["country"]) \
        .with_near_text({"concepts": [query]}) \
        .with_limit(num_results) \
        .do()

    countries = [res['country'] for res in response['data']['Get']['DetailedCountry22']]

    return jsonify({"related_countries": countries})

if __name__ == '__main__':
    app.run(debug=True)