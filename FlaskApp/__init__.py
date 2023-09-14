from flask import Flask, request, redirect, render_template, jsonify
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import json
import os
import requests
import base64
import re
import sys
import logging

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', filename='bot.log', encoding='utf-8', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
handler = logging.StreamHandler(sys.stdout)
logging.getLogger().addHandler(handler)

# Get Storage Account details from environment
STORAGE_ACCOUNT_CONNECTION_STRING = os.environ["STORAGE_ACCOUNT_CONNECTION_STRING"]
AZURE_DEVOPS_PAT = os.environ["AZURE_DEVOPS_PAT"]
AZURE_DEVOPS_PIPELINE_ID = os.environ["AZURE_DEVOPS_PIPELINE_ID"]
AZURE_DEVOPS_PROJECT_NAME = os.environ["AZURE_DEVOPS_PROJECT_NAME"]
AZURE_DEVOPS_ORGANIZATION_NAME = os.environ["AZURE_DEVOPS_ORGANIZATION_NAME"]

def trigger_pipeline(personal_access_token, organization_name, project_name, pipeline_id):
    personal_access_token = personal_access_token.encode('ascii')
    personal_access_token = base64.b64encode(personal_access_token)
    personal_access_token = personal_access_token.decode('ascii')

    url = f"https://dev.azure.com/{organization_name}/{project_name}/_apis/pipelines/{pipeline_id}/runs?api-version=7.0&Content-Type=application/json"

    payload = json.dumps({
      "resources": {
        "repositories": {
          "self": {
            "refName": "refs/heads/main"
          }
        }
      }
    })
    headers = {
      'Content-Type': 'application/json',
      'Authorization': f'Basic {personal_access_token}',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        print("Pipeline triggered successfully.")
    else:
        print(f"Failed to trigger the pipeline. Status code: {response.status_code}")
        print(response.json)


# Initialize the connection to Azure storage account
blob_service_client = BlobServiceClient.from_connection_string(STORAGE_ACCOUNT_CONNECTION_STRING)
container_name = "json"
json_file_name = 'managed_identities.tfvars.json'

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        logging.info("Received JSON data: %s", request.json)
        data = request.json

        managed_identities = data.get('identities', [])

        logging.info("Final managed identities: %s", managed_identities)


        # Upload file to Azure Blob Storage
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(json_file_name)
        blob_client.upload_blob(json.dumps(managed_identities, indent=4), overwrite=True)

        # Trigger Terraform
        trigger_pipeline(AZURE_DEVOPS_PAT, AZURE_DEVOPS_ORGANIZATION_NAME, AZURE_DEVOPS_PROJECT_NAME, AZURE_DEVOPS_PIPELINE_ID)

        return jsonify({"status": "success"})

    # Read the JSON file from Azure Blob Storage and populate the HTML form
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(json_file_name)
    try:
        blob_data = blob_client.download_blob()
        managed_identities = json.loads(blob_data.readall().decode('utf-8'))
    except Exception as e:
        logging.error(f"Error reading blob: {e}")
        managed_identities = []

    return render_template('index.html', managed_identities=managed_identities)


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         logging.info(request.form)
#         data = request.form

#         for key, value in data.items():
#           logging.info(f"{key}: {value}")

#         managed_identities = []
#         id_count = int(data.get('id_count'))
#         for i in range(1, id_count + 1):
#             identity_id = data.get(f'id_{i}')
#             roles_count = int(data.get(f'roles_count_{i}'))
#             roles = []
#             for j in range(1, roles_count + 1):
#                 roles.append({
#                     "scope": data.get(f'scope_{i}_{j}'),
#                     "role_definition_name": data.get(f'role_definition_{i}_{j}'),
#                     "description": data.get(f'description_{i}_{j}')
#                 })
#             managed_identities.append({
#                 "id": identity_id,
#                 "roles": roles
#             })

#         # Upload file to Azure Blob Storage
#         container_client = blob_service_client.get_container_client(container_name)
#         blob_client = container_client.get_blob_client(json_file_name)
#         blob_client.upload_blob(json.dumps(managed_identities, indent=4), overwrite=True)

#         # Trigger Terraform
#         trigger_pipeline(AZURE_DEVOPS_PAT, AZURE_DEVOPS_ORGANIZATION_NAME, AZURE_DEVOPS_PROJECT_NAME, AZURE_DEVOPS_PIPELINE_ID)

#         return redirect('/')

#     # Read the JSON file from Azure Blob Storage and populate the HTML form
#     container_client = blob_service_client.get_container_client(container_name)
#     blob_client = container_client.get_blob_client(json_file_name)
#     try:
#         blob_data = blob_client.download_blob()
#         managed_identities = json.loads(blob_data.readall().decode('utf-8'))
#     except:
#         managed_identities = []

#     return render_template('index.html', managed_identities=managed_identities)

if __name__ == '__main__':
    app.run(debug=True)
