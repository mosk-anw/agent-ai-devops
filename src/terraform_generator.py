import json
import subprocess

from src.config import TERRAFORM_MCP_SERVER_URL

def get_resource_schema_from_mcp(resource_type):
    try:
        resource_type_map = {
            "resource group": "Microsoft.Resources/resourceGroups",
            "virtual machine": "Microsoft.Compute/virtualMachines",
            "storage account": "Microsoft.Storage/storageAccounts",
            "API gateway": "Microsoft.ApiManagement/service",
        }
        
        bicep_resource_type = resource_type_map.get(resource_type)
        if not bicep_resource_type:
            print(f"Error: No Bicep resource type mapping for {resource_type}")
            return None

        # Execute the npx command to get the Bicep schema
        command = ["npx", "-y", "@azure/mcp@latest", "bicepschema", "get", "--resource-type", bicep_resource_type]
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"DEBUG: npx stdout: {process.stdout}")
        print(f"DEBUG: npx stderr: {process.stderr}")
        
        mcp_response = json.loads(process.stdout)
        print(f"DEBUG: MCP Response: {mcp_response}")
        
        if mcp_response.get("error"):
            print(f"Error from Azure MCP: {mcp_response['error']}")
            return None

        bicep_schema = mcp_response["results"]["BicepSchemaResult"][0]["bodyType"]
        print(f"DEBUG: Bicep Schema: {bicep_schema}")

        # Simplified parsing of Bicep schema to agent's schema format
        schema = {}
        properties = bicep_schema.get("properties", {})

        for prop_dict in properties:
            prop_name = prop_dict.get("name")
            prop_details = prop_dict # Use the whole dictionary for details

            # Basic extraction for common properties
            if prop_name == "name":
                schema["name"] = {"type": "string", "required": True, "prompt": f"What would you like to name the {resource_type}?"}
            elif prop_name == "location":
                schema["location"] = {"type": "string", "required": True, "prompt": "What Azure region should it be created in? (e.g., eastus, westus2)"}
            elif prop_name == "resourceGroup": # Bicep uses resourceGroup, Terraform uses resource_group_name
                schema["resource_group_name"] = {"type": "string", "required": True, "prompt": "What is the name of the resource group?"}
            # Add more property parsing as needed for other resource types
            # This is a very simplified parser and will need to be expanded

        # Add specific properties based on resource type (if not found in Bicep schema or for simplicity)
        if resource_type == "virtual machine":
            if "os_image" not in schema: schema["os_image"] = {"type": "string", "required": True, "prompt": "What OS image should it use? (e.g., UbuntuServer, WindowsServer)"}
            if "size" not in schema: schema["size"] = {"type": "string", "required": True, "prompt": "What size should the VM be? (e.g., Standard_B1s, Standard_DS1_v2)"}
        elif resource_type == "storage account":
            if "account_tier" not in schema: schema["account_tier"] = {"type": "string", "required": True, "prompt": "What account tier? (e.g., Standard, Premium)"}
            if "account_replication_type" not in schema: schema["account_replication_type"] = {"type": "string", "required": True, "prompt": "What replication type? (e.g., LRS, GRS, RAGRS, ZRS)"}
        elif resource_type == "API gateway":
            if "publisher_email" not in schema: schema["publisher_email"] = {"type": "string", "required": True, "prompt": "What is the publisher email for the API Gateway?"}
            if "publisher_name" not in schema: schema["publisher_name"] = {"type": "string", "required": True, "prompt": "What is the publisher name for the API Gateway?"}

        return schema

    except subprocess.CalledProcessError as e:
        print(f"Error executing npx command: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from npx output: {e}")
        return None
    except Exception as e:
        print(f"Error getting resource schema from MCP: {e}")
        return None

def generate_terraform_code(resource_type, parameters):
    tf_code = ""

    # Generate Terraform based on resource type
    if resource_type == "resource group":
        name = parameters.get("name")
        location = parameters.get("location")
        tf_code = f"""
resource \"azurerm_resource_group\" \"main\" {{
  name     = \"{name}\" 
  location = \"{location}\" 
}}"""
    elif resource_type == "virtual machine":
        vm_name = parameters.get("name")
        os_image = parameters.get("os_image")
        vm_size = parameters.get("size")
        vm_location = parameters.get("location")
        resource_group_name = parameters.get("resource_group_name")

        tf_code = f"""
resource \"azurerm_resource_group\" \"vm_rg\" {{
  name     = \"{resource_group_name}\" 
  location = \"{vm_location}\" 
}}

resource \"azurerm_virtual_network\" \"vm_vnet\" {{
  name                = \"{vm_name}-vnet\"
  address_space       = [\"10.0.0.0/16\"]
  location            = azurerm_resource_group.vm_rg.location
  resource_group_name = azurerm_resource_group.vm_rg.name
}}

resource \"azurerm_subnet\" \"vm_subnet\" {{
  name                 = \"{vm_name}-subnet\"
  resource_group_name  = azurerm_resource_group.vm_rg.name
  virtual_network_name = azurerm_virtual_network.vm_vnet.name
  address_prefixes     = [\"10.0.1.0/24\"]
}}

resource \"azurerm_network_interface\" \"vm_nic\" {{
  name                = \"{vm_name}-nic\"
  location            = azurerm_resource_group.vm_rg.location
  resource_group_name = azurerm_resource_group.vm_rg.name

  ip_configuration {{
    name                          = \"internal\"
    subnet_id                     = azurerm_subnet.vm_subnet.id
    private_ip_address_allocation = \"Dynamic\"
  }}
}}

resource \"azurerm_linux_virtual_machine\" \"main\" {{
  name                  = \"{vm_name}\" 
  resource_group_name   = azurerm_resource_group.vm_rg.name
  location              = azurerm_resource_group.vm_rg.location
  size                  = \"{vm_size}\" 
  admin_username        = \"azureuser\"
  network_interface_ids = [azurerm_network_interface.vm_nic.id]

  os_disk {{
    caching              = \"ReadWrite\"
    storage_account_type = \"Standard_LRS\"
  }}

  source_image_reference {{
    publisher = \"Canonical\"
    offer     = \"UbuntuServer\"
    sku       = \"{os_image}\" 
    version   = \"latest\"
  }}

  admin_ssh_key {{
    username   = \"azureuser\"
    public_key = \"ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD3b3+...\"
  }}
}}
"""
    elif resource_type == "storage account":
        name = parameters.get("name")
        location = parameters.get("location")
        account_tier = parameters.get("account_tier")
        account_replication_type = parameters.get("account_replication_type")
        resource_group_name = parameters.get("resource_group_name")
        tf_code = f"""
resource \"azurerm_resource_group\" \"storage_rg\" {{
  name     = \"{resource_group_name}\" 
  location = \"{location}\" 
}}

resource \"azurerm_storage_account\" \"main\" {{
  name                     = \"{name}\" 
  resource_group_name      = azurerm_resource_group.storage_rg.name
  location                 = azurerm_resource_group.storage_rg.location
  account_tier             = \"{account_tier}\" 
  account_replication_type = \"{account_replication_type}\" 
}}
"""
    elif resource_type == "API gateway":
        name = parameters.get("name")
        resource_group_name = parameters.get("resource_group_name")
        location = parameters.get("location")
        publisher_email = parameters.get("publisher_email")
        publisher_name = parameters.get("publisher_name")
        tf_code = f"""
resource \"azurerm_api_management\" \"main\" {{
  name                = \"{name}\" 
  location            = \"{location}\" 
  resource_group_name = \"{resource_group_name}\" 
  publisher_name      = \"{publisher_name}\" 
  publisher_email     = \"{publisher_email}\" 

  sku_name = \"Developer_1\" 
}}
"""
    else:
        tf_code = "# Unknown resource type, no Terraform code generated.\n"
    return tf_code
