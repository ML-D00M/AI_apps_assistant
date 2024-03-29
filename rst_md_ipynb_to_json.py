import os
import json
from docutils.core import publish_doctree
from docutils import nodes
from docutils.parsers.rst import directives
import nbformat
from nbconvert import MarkdownExporter

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

def md_to_json(md_file):
    with open(md_file, 'r', encoding='utf-8') as file:
        content = file.read()
    # Convert Markdown to simplified JSON structure here
    # For example:
    simplified = {'content': content}
    return simplified

def ipynb_to_json(ipynb_file):
    with open(ipynb_file, 'r', encoding='utf-8') as file:
        nb = nbformat.read(file, as_version=4)
        exporter = MarkdownExporter()
        body, _ = exporter.from_notebook_node(nb)
    # Convert notebook Markdown to simplified JSON structure here
    # For example:
    simplified = {'content': body}
    return simplified

def process_directory(directory):
    aggregated_content = {}
    for root, dirs, files in os.walk(directory):
        for filename in files:
            full_path = os.path.join(root, filename)
            relative_path = os.path.relpath(full_path, directory)
            simplified_content = None 

            if filename.endswith('.rst'):
                simplified_content = rst_to_json(full_path)
            elif filename.endswith('.md'):
                simplified_content = md_to_json(full_path)
            elif filename.endswith('.ipynb'):
                simplified_content = ipynb_to_json(full_path)

            aggregated_content[relative_path] = simplified_content

    return aggregated_content

def process_directory_2(directory, output_folder):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            # Process each directory
            aggregated_content = process_directory(item_path)
            # Use the directory name as the filename
            output_file = os.path.join(output_folder, f"{item}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(aggregated_content, f, indent=4)
        else:
            # Process individual files at the root level of the directory
            if item.endswith(('.rst', '.md', '.ipynb')):
                if item.endswith('.rst'):
                    simplified_content = rst_to_json(item_path)
                elif item.endswith('.md'):
                    simplified_content = md_to_json(item_path)
                elif item.endswith('.ipynb'):
                    simplified_content = ipynb_to_json(item_path)
                
                output_file = os.path.join(output_folder, f"{os.path.splitext(item)[0]}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(simplified_content, f, indent=4)


if __name__ == "__main__":
    docs_directory = '.\\llama_index_repo\\llama_index\\docs'  # Adjust as needed
    output_directory = '.\\llamaindex_docs'  # Output directory for JSON files
    process_directory_2(docs_directory, output_directory)
    print(f"Documentation has been split into individual JSON files within {output_directory}")