import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TERRAFORM_MCP_SERVER_URL = "http://localhost:8081/mcp"
CLOUD_RESOURCES_REPO_PATH = "/Users/shaik/POC_DEVOPS_AGENT/cloud-resources"
