import os
import json
from docutils.core import publish_doctree
from docutils import nodes
from docutils.parsers.rst import directives

# Register any custom directives if needed, for example:
# directives.register_directive('toctree', directives.misc.Include)

def rst_to_json(rst_file):
    with open(rst_file, 'r', encoding='utf-8') as file:
        content = file.read()
    doctree = publish_doctree(content)
    # Initialize your simplified structure
    simplified = []  # Customize this structure based on the .rst content you need to extract

    # Add our logic here to traverse the doctree and populate the simplified structure
    # Example: simplified.append({'section': section_node.astext(), 'content': content_node.astext()})
    
    def extract_text(node):
        text_content = ''
        if isinstance(node, nodes.Text):
            # Filter out the error messages
            text = node.astext()
            # Check for error messages related to unknown directives and ignore them
            if "Unknown directive type" in text or "No directive entry" in text:
                return ''
            else:
                return text
        elif isinstance(node, nodes.literal_block):
            # For handling code blocks — preserve the entire literal block text as it is.
            code_text = node.astext()
            # Check for error messages within code blocks and ignore them
            if "Unknown directive type" in code_text or "No directive entry" in code_text:
                return ''
            else:
                # If no error messages, wrap with triple backticks
                return '```' + code_text + '```'  # Mark code blocks with triple backticks
        elif isinstance(node, (nodes.bullet_list, nodes.enumerated_list, nodes.list_item)):
            # Handle bullet lists, enumerated lists, and list items
            items = []
            for child in node.children:
                item_text = extract_text(child)
                if item_text.strip():
                    # Append items with a bullet point
                    items.append(item_text.strip())
            text_content = '\n'.join(items)
        else:
            for child in node.children:
                text_content += extract_text(child)
        return text_content.strip()

    def visit_node(node):
        node_data = {}
        if isinstance(node, nodes.section):
            node_data['title'] = node.next_node(nodes.title).astext() if node.next_node(nodes.title) else ''
            node_data['content'] = []
            node_data['sections'] = []

            for child in node.children:
                child_text = extract_text(child)
                if child_text:
                    # Append non-empty text
                    node_data['content'].append(child_text)
                if isinstance(child, nodes.section):
                    # Handle subsections
                    node_data['sections'].append(visit_node(child))
        return node_data

    for child in doctree.traverse():
        if isinstance(child, nodes.section):
            simplified.append(visit_node(child))

    return simplified


def process_directory(directory):
    aggregated_content = {}
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.rst'):
                full_path = os.path.join(root, filename)
                simplified_content = rst_to_json(full_path)
                relative_path = os.path.relpath(full_path, directory)
                aggregated_content[relative_path] = simplified_content

    return aggregated_content

if __name__ == "__main__":
    directory = '.\llama_index_repo\llama_index\docs'  # Adjust as needed
    aggregated_content = process_directory(directory)
    output_file = 'aggregated_documentation.json'  # This file will be created in the same directory as the script
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(aggregated_content, f, indent=4)
    print(f"All documentation has been consolidated into {output_file}")