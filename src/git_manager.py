import os
import subprocess
from src.config import CLOUD_RESOURCES_REPO_PATH

def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(e.cmd)}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"Error: Command not found. Please ensure 'git' and 'gh' are installed and in your PATH.")
        return False

def handle_git_operations(feature_branch_name, file_content, target_file_path):
    # Ensure the cloud-resources directory exists and is a git repo
    if not os.path.exists(os.path.join(CLOUD_RESOURCES_REPO_PATH, ".git")):
        print(f"Cloning cloud-resources repository into {CLOUD_RESOURCES_REPO_PATH}...")
        if not run_command(["git", "clone", "https://github.com/mosk-anw/cloud-resources.git", CLOUD_RESOURCES_REPO_PATH]):
            return
    else:
        print(f"cloud-resources repository already exists at {CLOUD_RESOURCES_REPO_PATH}. Fetching latest changes...")
        if not run_command(["git", "fetch", "origin"], cwd=CLOUD_RESOURCES_REPO_PATH):
            return
        if not run_command(["git", "checkout", "main"], cwd=CLOUD_RESOURCES_REPO_PATH):
            return
        if not run_command(["git", "pull", "origin", "main"], cwd=CLOUD_RESOURCES_REPO_PATH):
            return

    # Create and switch to a new branch
    print(f"Creating and switching to branch: {feature_branch_name}")
    if not run_command(["git", "checkout", "-b", feature_branch_name], cwd=CLOUD_RESOURCES_REPO_PATH):
        return

    # Ensure the target directory exists
    full_target_path = os.path.join(CLOUD_RESOURCES_REPO_PATH, target_file_path)
    os.makedirs(os.path.dirname(full_target_path), exist_ok=True)

    # Write the content to the file
    print(f"Writing content to {full_target_path}")
    with open(full_target_path, "w") as f:
        f.write(file_content)

    # Add and commit the changes
    print("Adding and committing changes...")
    if not run_command(["git", "add", "."], cwd=CLOUD_RESOURCES_REPO_PATH):
        return
    if not run_command(["git", "commit", "-m", f"Feat: {feature_branch_name}"], cwd=CLOUD_RESOURCES_REPO_PATH):
        return

    # Push the branch
    print(f"Pushing branch: {feature_branch_name}")
    if not run_command(["git", "push", "-u", "origin", feature_branch_name], cwd=CLOUD_RESOURCES_REPO_PATH):
        return

    # Create a Pull Request using gh CLI
    pr_title = f"Feat: {feature_branch_name}"
    pr_body = f"This PR adds {target_file_path} as requested by the AI agent."
    print(f"Creating Pull Request...")
    if not run_command(["gh", "pr", "create", "--base", "main", "--head", feature_branch_name, "--title", pr_title, "--body", pr_body, "--repo", "mosk-anw/cloud-resources"]):
        return

    print("Git operations completed. A Pull Request has been created.")