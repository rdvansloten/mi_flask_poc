# MI Flask POC
This is a proof-of-concept for a service portal that allows users to create Managed Identities via a web interface. The portal is built using Flask and the Azure SDK for Python.

## Getting Started
The repository must be deployed to an Azure Function App. The Function App must be configured with the following environment variables:

| Name                              | Description                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------- |
| STORAGE_ACCOUNT_CONNECTION_STRING | Connection string for the Storage Account that will be used to store the Managed Identity information |
| AZURE_DEVOPS_PAT                  | Personal Access Token for the Azure DevOps account that will start the pipeline                       |
| AZURE_DEVOPS_PIPELINE_ID          | ID of the pipeline that will be started                                                               |
| AZURE_DEVOPS_PROJECT_NAME         | Name of the Azure DevOps project that contains the pipeline                                           |
| AZURE_DEVOPS_ORGANIZATION_NAME    | Name of the Azure DevOps organization that contains the project                                       |

## Deployment
You can deploy the app to an Azure Function through the pipeline at [pipelines/deploy-flask-app.yaml](./pipelines/deploy-flask-app.yaml) by filling out the appropriate `app` and `rg` values.

## Terraform
The Azure Function app will write to a json file and kick off a Terraform pipeline using the PAT and pipeline ID provided in the environment variables. The Terraform pipeline in [pipelines/run-terraform.yaml](.pipelines/run-terraform.yaml) will then consume the json file and create the Managed Identities.