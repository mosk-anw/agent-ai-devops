import requests
import json
import subprocess


def get_azure_locations():
    try:
        # Execute the npx command to get Azure locations
        command = ["npx", "-y", "@azure/mcp@latest", "extension", "az", "--command", "account list-locations"]
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # Parse the JSON output, handling potential non-JSON output
        output_str = process.stdout.strip()
        json_start = output_str.find('{')
        json_end = output_str.rfind('}')
        
        if json_start == -1 or json_end == -1:
            print(f"Error: Could not find JSON in npx output: {output_str}")
            return []

        json_str = output_str[json_start : json_end + 1]
        output = json.loads(json_str)
        
        locations = []
        if output and output.get("results"):
            for loc in output["results"]:
                if loc.get("name"):
                    locations.append(loc["name"])
        return locations
    except subprocess.CalledProcessError as e:
        print(f"Error executing npx command: {e.stderr}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from npx output: {e}")
        return []
    except Exception as e:
        print(f"Error getting Azure locations: {e}")
        return []
