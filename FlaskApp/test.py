import requests
import base64
import json

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

trigger_pipeline(":72tpkmsmr7b3korkx53xbogosyecivnonzd6kfxybr2buunmbbea", "rdvansloten", "Automation", "28")