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

data "azurerm_user_assigned_identity" "app" {
  name                = "id-coffre-mdp"
  resource_group_name = data.azurerm_resource_group.lab.name
}

data "azurerm_container_registry" "acr" {
  name                = "coffremdpacr"
  resource_group_name = data.azurerm_resource_group.lab.name
}

resource "azurerm_container_group" "coffre_mdp" {
  identity {
    type         = "UserAssigned"
    identity_ids = [data.azurerm_user_assigned_identity.app.id]
  }
  name                = "coffre-mdp-app"
  location            = data.azurerm_resource_group.lab.location
  resource_group_name = data.azurerm_resource_group.lab.name
  os_type             = "Linux"
  ip_address_type     = "Public"
  dns_name_label      = "coffre-mdp-joel"

  image_registry_credential {
    server   = data.azurerm_container_registry.acr.login_server
    username = data.azurerm_container_registry.acr.admin_username
    password = trimspace(data.azurerm_container_registry.acr.admin_password)
  }

  container {
    name   = "coffre-mdp"
    image  = "${data.azurerm_container_registry.acr.login_server}/coffre-mdp:latest"
    cpu    = "0.5"
    memory = "1.0"

    ports {
      port     = 8080
      protocol = "TCP"
    }
    environment_variables = {
      AZURE_CLIENT_ID = "570d85d9-4435-4730-9f7f-fabb84279d3c"
    }
  }
}

output "app_url" {
  value = "http://${azurerm_container_group.coffre_mdp.fqdn}:8080"
}
