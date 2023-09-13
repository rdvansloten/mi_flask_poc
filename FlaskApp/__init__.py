from flask import Flask, request, redirect, render_template, jsonify
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import json
import os

# Get Storage Account details from environment
STORAGE_ACCOUNT_CONNECTION_STRING = os.environ["STORAGE_ACCOUNT_CONNECTION_STRING"]

# Initialize the connection to Azure storage account
blob_service_client = BlobServiceClient.from_connection_string(STORAGE_ACCOUNT_CONNECTION_STRING)
container_name = "json"
json_file_name = 'managed_identities.tfvars.json'

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form
        managed_identities = []
        id_count = int(data.get('id_count'))
        for i in range(1, id_count + 1):
            identity_id = data.get(f'id_{i}')
            roles_count = int(data.get(f'roles_count_{i}'))
            roles = []
            for j in range(1, roles_count + 1):
                roles.append({
                    "scope": data.get(f'scope_{i}_{j}'),
                    "role_definition_name": data.get(f'role_definition_{i}_{j}'),
                    "description": data.get(f'description_{i}_{j}')
                })
            managed_identities.append({
                "id": identity_id,
                "roles": roles
            })

        # Upload file to Azure Blob Storage
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(json_file_name)
        blob_client.upload_blob(json.dumps(managed_identities, indent=4), overwrite=True)

        return redirect('/')

    # Read the JSON file from Azure Blob Storage and populate the HTML form
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(json_file_name)
    try:
        blob_data = blob_client.download_blob()
        managed_identities = json.loads(blob_data.readall().decode('utf-8'))
    except:
        managed_identities = []

    return render_template('index.html', managed_identities=managed_identities)

if __name__ == '__main__':
    app.run(debug=True)
