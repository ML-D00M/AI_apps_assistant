# Split a large JSON by the top-level keys file into smaller ones 
# that are manageable for a custom GPT.

import json

def split_json(json_file, max_size_mb=1):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Assuming 'data' is a dictionary, we'll split it by top-level keys
    # If 'data' is a list, you might need to split by a number of items
    keys = list(data.keys())
    chunk = {}
    size = 0
    part = 1

    for key in keys:
        chunk[key] = data[key]
        size += len(json.dumps(chunk))

        # Check if the size of the chunk in bytes is larger than the max allowed size
        if size > max_size_mb * 1024 * 1024:  
            with open(f'smaller_part_{part}.json', 'w', encoding='utf-8') as f:
                json.dump(chunk, f, indent=4)
            part += 1
            chunk = {}
            size = 0

    # Don't forget to save the last chunk if it's not empty
    if chunk:
        with open(f'smaller_part_{part}.json', 'w', encoding='utf-8') as f:
            json.dump(chunk, f, indent=4)

# Example usage
split_json('llamaindex_aggregated_documentation.json')
