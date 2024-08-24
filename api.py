import os
from dotenv import load_dotenv
import requests
from flask import Flask, request, jsonify

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route('/api/create-issue', methods=['POST'])
def create_issue():
    data = request.json

    # Extract the required fields from the request
    title = data.get('title')
    description = data.get('description')
    user_label_selection = data.get('user_label_selection')
    email = data.get('email', None)

    # Get the API key and other sensitive data from environment variables
    api_key = os.getenv("LINEAR_API_KEY")
    team_id = os.getenv("LINEAR_TEAM_ID")

    # Validate that the API key and team ID are set
    if not api_key or not team_id:
        return jsonify({"error": "API key or team ID not set in environment variables"}), 500

    always_present_label_id = "59f1342b-9ba3-4168-b3f6-a097a3de40af"
    labels = {
        "ACE": "cbef7a2c-1a77-4a5c-b214-39188924d63f",
        "Control Room": "0d0d9e0b-f2ef-42b4-8131-b5fa4f530086",
        "Workroom UI": "dd51de8b-6f12-47a4-94a8-73b090b0303e"
    }

    # Validate user selection
    if user_label_selection not in labels:
        return jsonify({"error": "Invalid label selection"}), 400

    selected_label_id = labels[user_label_selection]

    # Construct the issue description
    issue_description = description
    if email:
        issue_description += f"\n\nReported by: {email}"

    # Construct the mutation
    mutation = {
        "query": """
        mutation IssueCreate($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    title
                }
            }
        }
        """,
        "variables": {
            "input": {
                "title": title,
                "description": issue_description,
                "teamId": team_id,
                "labelIds": [always_present_label_id, selected_label_id]
            }
        }
    }

    # Make the request to Linear API
    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key  # No 'Bearer' prefix
    }
    response = requests.post('https://api.linear.app/graphql', json=mutation, headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": response.text}), response.status_code

if __name__ == '__main__':
    app.run()