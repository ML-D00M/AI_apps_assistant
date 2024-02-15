import json
import os

def split_json(json_file, output_directory):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Iterate over the items and aggregate content by top-level directory
    for top_level_key, contents in data.items():
        # Sanitize the top-level key to be used as part of the filename
        sanitized_key = top_level_key.replace('\\', '_').replace('/', '_').replace(':', '_')
        output_file_path = os.path.join(output_directory, f"{sanitized_key}.json")

        # Aggregate content for the top-level directory
        aggregated_content = {top_level_key: contents}

        # Write aggregated content to a single JSON file per top-level directory
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(aggregated_content, f, indent=4)

def split_json_equally(json_file, output_directory, num_files=10):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Flatten the data to a list if it's a dictionary
    if isinstance(data, dict):
        data = list(data.values())
    
    # Calculate the size of each segment
    total_items = len(data)
    items_per_file = total_items // num_files
    if total_items % num_files:
        items_per_file += 1  # Handle any remainder by increasing items per file

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Split data into num_files parts and write each to a file
    for i in range(num_files):
        segment = data[i*items_per_file:(i+1)*items_per_file]
        output_file_path = os.path.join(output_directory, f"examples_part_{i+1}.json")
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(segment, f, indent=4)


# Usage
output_directory = 'llamaindex_docs'  # Set to your desired output directory
split_json_equally('./llamaindex_docs/examples.json', output_directory, num_files=10)
