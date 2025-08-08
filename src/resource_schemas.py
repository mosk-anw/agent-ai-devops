# src/resource_schemas.py

RESOURCE_GROUP_SCHEMA = {
    "name": {"type": "string", "required": True, "prompt": "What would you like to name the resource group?"},
    "location": {"type": "string", "required": True, "prompt": "What Azure region should it be created in? (e.g., eastus, westus2)"},
}

VIRTUAL_MACHINE_SCHEMA = {
    "name": {"type": "string", "required": True, "prompt": "What would you like to name the virtual machine?"},
    "os_image": {"type": "string", "required": True, "prompt": "What OS image should it use? (e.g., UbuntuServer, WindowsServer)"},
    "size": {"type": "string", "required": True, "prompt": "What size should the VM be? (e.g., Standard_B1s, Standard_DS1_v2)"},
    "location": {"type": "string", "required": True, "prompt": "What Azure region should it be created in? (e.g., eastus, westus2)"},
}

STORAGE_ACCOUNT_SCHEMA = {
    "name": {"type": "string", "required": True, "prompt": "What would you like to name the storage account? (must be globally unique)"},
    "location": {"type": "string", "required": True, "prompt": "What Azure region should it be created in? (e.g., eastus, westus2)"},
    "account_tier": {"type": "string", "required": True, "prompt": "What account tier? (e.g., Standard, Premium)"},
    "account_replication_type": {"type": "string", "required": True, "prompt": "What replication type? (e.g., LRS, GRS, RAGRS, ZRS)"},
}

# Map resource types to their schemas
RESOURCE_SCHEMAS = {
    "resource group": RESOURCE_GROUP_SCHEMA,
    "virtual machine": VIRTUAL_MACHINE_SCHEMA,
    "storage account": STORAGE_ACCOUNT_SCHEMA,
}
