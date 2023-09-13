from flask import Flask, request, redirect, render_template, jsonify
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import json
import os

# Get Storage Account details from environment
STORAGE_ACCOUNT_CONNECTION_STRING = os.environ["STORAGE_ACCOUNT_CONNECTION_STRING"]

# Initialize the connection to Azure storage account
blob_service_client = BlobServiceClient.from_connection_string(STORAGE_ACCOUNT_CONNECTION_STRING)
container_name = "json"

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
        
        # Convert the Python dictionary to a JSON string
        json_data = json.dumps(managed_identities, indent=4)
        
        # Convert the JSON string to bytes
        json_bytes = json_data.encode('utf-8')

        # Upload data to Azure Blob Storage
        json_file_name = 'managed_identities.tfvars.json'
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(json_file_name)
        
        blob_client.upload_blob(json_bytes, overwrite=True)

        return redirect('/')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)