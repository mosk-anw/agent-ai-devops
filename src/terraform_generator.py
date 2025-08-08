from src.resource_schemas import RESOURCE_SCHEMAS

def generate_terraform_code(resource_type, parameters):
    tf_code = ""
    schema = RESOURCE_SCHEMAS.get(resource_type)

    if not schema:
        return f"# Error: No schema defined for resource type: {resource_type}\n"

    # Generate Terraform based on resource type
    if resource_type == "resource group":
        name = parameters.get("name")
        location = parameters.get("location")
        tf_code = f"""
resource "azurerm_resource_group" "main" {{
  name     = "{name}"
  location = "{location}"
}}
"""
    elif resource_type == "virtual machine":
        vm_name = parameters.get("name")
        os_image = parameters.get("os_image")
        vm_size = parameters.get("size")
        vm_location = parameters.get("location")

        # For simplicity, we'll hardcode a resource group and network interface for now.
        # In a real scenario, these would be dynamically created or referenced.
        tf_code = f"""
resource "azurerm_resource_group" "vm_rg" {{
  name     = "{vm_name}-rg"
  location = "{vm_location}"
}}

resource "azurerm_virtual_network" "vm_vnet" {{
  name                = "{vm_name}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.vm_rg.location
  resource_group_name = azurerm_resource_group.vm_rg.name
}}

resource "azurerm_subnet" "vm_subnet" {{
  name                 = "{vm_name}-subnet"
  resource_group_name  = azurerm_resource_group.vm_rg.name
  virtual_network_name = azurerm_virtual_network.vm_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}}

resource "azurerm_network_interface" "vm_nic" {{
  name                = "{vm_name}-nic"
  location            = azurerm_resource_group.vm_rg.location
  resource_group_name = azurerm_resource_group.vm_rg.name

  ip_configuration {{
    name                          = "internal"
    subnet_id                     = azurerm_subnet.vm_subnet.id
    private_ip_address_allocation = "Dynamic"
  }}
}}

resource "azurerm_linux_virtual_machine" "main" {{
  name                  = "{vm_name}"
  resource_group_name   = azurerm_resource_group.vm_rg.name
  location              = azurerm_resource_group.vm_rg.location
  size                  = "{vm_size}"
  admin_username        = "azureuser"
  network_interface_ids = [azurerm_network_interface.vm_nic.id]

  os_disk {{
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }}

  source_image_reference {{
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "{os_image}"
    version   = "latest"
  }}

  admin_ssh_key {{
    username   = "azureuser"
    public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD3b3+..."
  }}
}}
"""
    elif resource_type == "storage account":
        name = parameters.get("name")
        location = parameters.get("location")
        account_tier = parameters.get("account_tier")
        account_replication_type = parameters.get("account_replication_type")
        tf_code = f"""
resource "azurerm_resource_group" "storage_rg" {{
  name     = "{name}-rg"
  location = "{location}"
}}

resource "azurerm_storage_account" "main" {{
  name                     = "{name}"
  resource_group_name      = azurerm_resource_group.storage_rg.name
  location                 = azurerm_resource_group.storage_rg.location
  account_tier             = "{account_tier}"
  account_replication_type = "{account_replication_type}"
}}
"""
    else:
        tf_code = "# Unknown resource type, no Terraform code generated.\n"
    return tf_code
