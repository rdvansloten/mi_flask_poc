resource "azurerm_resource_group" "main" {
  name     = "mi_storage_poc"
  location = "westeurope"
}

data "http" "get_json" {
  url = "https://miflaskpocjsonstorage.blob.core.windows.net/json/managed_identities.tfvars.json"

  request_headers = {
    Accept = "application/json"
  }
}

data "azurerm_client_config" "current" {}

resource "azurerm_user_assigned_identity" "main" {
  for_each = { for item in local.json_data : item.id => item }

  name                = each.value.id
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}

resource "azurerm_role_assignment" "main" {
  for_each = { for idx, assignment in flatten(local.role_assignments) : format("%s-%s", assignment.identity_id, idx) => assignment }

  principal_id         = azurerm_user_assigned_identity.main[each.value.identity_id].principal_id
  role_definition_name = each.value.role_definition_name
  scope                = each.value.scope
  description          = "${each.value.description} - Created by Object ID '${data.azurerm_client_config.current.object_id}'"
}

locals {
  json_data = jsondecode(data.http.get_json.response_body)

  role_assignments = [
    for identity in local.json_data : [
      for role in identity.roles : {
        identity_id          = identity.id
        role_definition_name = role.role_definition
        scope                = role.scope
        description          = role.description
      }
    ]
  ]
}