import os
import subprocess
import yaml
import json

# Get all environment variables
env_vars = os.environ['ALLSECRETS']

def print_all_keys(data, prefix=""):
    if isinstance(data, dict):
        for key, value in data.items():
            print_all_keys(value, prefix + key + '.')
    elif isinstance(data, list):
        for i, item in enumerate(data):
            print_all_keys(item, prefix + str(i) + '.')
    else:
        print(prefix[:-1])  # Print the key without the trailing dot

def add_variables_to_env(file_path_old, file_path, variables):
    # Load the YAML file
    with open(file_path_old, 'r') as file:
        data = yaml.safe_load(file)

    # Add new variables to env
    if 'env' in data:
          for variable_name, variable_value in variables.items():
              data['env'][variable_name] = variable_value

    # Save the modified content back to the file
    with open(file_path, 'a') as file:
        yaml.dump(data, file, default_flow_style=False)

# Path to the YAML file
old_path = os.path.expanduser('~/workflow.yaml')
file_path = os.path.expanduser('~/.github/workflows/workflow.yaml')

print("PARSED JSON:")
parsed_data = json.loads(env_vars)
print_all_keys(parsed_data)

# Variables to add to env
# PYTHON_NAME: ${{ secrets.GITHUB_REPO_NAME }}
new_variables = {
    'VAR1': '${secrets.var1}',
    'VAR2': '${secrets.var2}'
}

# Call the function to add variables to env
add_variables_to_env(old_path, file_path, new_variables)

