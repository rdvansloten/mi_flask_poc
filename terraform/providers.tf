provider "azurerm" {
  features {}
}

terraform {
  backend "azurerm" {
    resource_group_name  = "mi_flask_poc"
    storage_account_name = "miflaskpocjsonstorage"
    container_name       = "tfstate"
    key                  = "mi_flask_poc.tfstate"
  }
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "> 3.0.0"
    }
  }
}