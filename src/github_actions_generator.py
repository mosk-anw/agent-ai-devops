# src/github_actions_generator.py

def generate_github_action_workflow(action_name, trigger, workflow_description):
    workflow_name = action_name.replace('-', ' ').title()
    
    workflow_yaml = f"""
name: {workflow_name}

on: [{trigger}]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Echo description
      run: echo "{workflow_description}"

    # Add more steps here based on workflow_description
    # This is a placeholder for actual build/deploy steps
    - name: Placeholder Step
      run: echo "This is a placeholder step for your workflow."
"""
    return workflow_yaml
