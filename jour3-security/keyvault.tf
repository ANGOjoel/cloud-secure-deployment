terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

data "azurerm_resource_group" "lab" {
  name = "rg-homelab-cloud"
}

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "coffre" {
  name                = "kv-coffre-mdp-joel"
  location            = data.azurerm_resource_group.lab.location
  resource_group_name = data.azurerm_resource_group.lab.name

  tenant_id = data.azurerm_client_config.current.tenant_id

  sku_name = "standard"

  purge_protection_enabled   = false
  soft_delete_retention_days = 7
}
resource "azurerm_key_vault_access_policy" "joel" {
  key_vault_id = azurerm_key_vault.coffre.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  secret_permissions = [
    "Get",
    "Set",
  ]
}
resource "azurerm_key_vault_access_policy" "application" {
  key_vault_id = azurerm_key_vault.coffre.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = "1e85974b-f2c4-47af-b534-cac4c9d5f385"

  secret_permissions = [
    "Get",
  ]
}
