import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MCP_SERVER_URL = "http://localhost:8080/mcp"
CLOUD_RESOURCES_REPO_PATH = "/Users/shaik/POC_DEVOPS_AGENT/cloud-resources"
