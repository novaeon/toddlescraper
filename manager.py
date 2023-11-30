import os
import json

# Get all environment variables
env_vars = os.environ['ALLSECRETS']
def get_all_keys(data, prefix="", keys_list=None):
    if keys_list is None:
        keys_list = []
    if isinstance(data, dict):
        for key, value in data.items():
            get_all_keys(value, prefix + key + '.', keys_list)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            get_all_keys(item, prefix + str(i) + '.', keys_list)
    else:
        keys_list.append(prefix[:-1])  # Add the key without the trailing dot to the list
    return keys_list

print("PARSED JSON:")
parsed_data = json.loads(env_vars)
jsonkeys = get_all_keys(parsed_data)
print(jsonkeys)

for jsonkey in jsonkeys:
    print(jsonkey)
