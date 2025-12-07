"""
Utility functions for AutoMetaRAG package.
"""

import json
import os
import re
from typing import Dict, List, Optional


def extract_json(text: str) -> List[Dict]:
    """
    Extract JSON objects from a text string, handling nested JSON.
    
    Args:
        text: Input text containing JSON objects
        
    Returns:
        List of parsed JSON objects
    """
    json_objects = []
    
    # Find all potential JSON objects by matching braces
    # This handles nested JSON by counting braces
    i = 0
    while i < len(text):
        if text[i] == '{':
            # Found start of potential JSON object
            brace_count = 0
            start = i
            
            # Find matching closing brace
            for j in range(i, len(text)):
                if text[j] == '{':
                    brace_count += 1
                elif text[j] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Found complete JSON object
                        potential_json = text[start:j+1]
                        try:
                            json_object = json.loads(potential_json)
                            json_objects.append(json_object)
                            i = j + 1
                            break
                        except json.JSONDecodeError:
                            # Not valid JSON, continue searching
                            i += 1
                            break
            else:
                # No matching brace found
                i += 1
        else:
            i += 1
    
    return json_objects


def save_json_to_file(data: Dict, filepath: str) -> None:
    """
    Save dictionary data to a JSON file.
    Creates directory if it doesn't exist.
    
    Args:
        data: Dictionary to save
        filepath: Path to output file
    """
    try:
        # Create directory if it doesn't exist (only if filepath has a directory)
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        # print(f"Data successfully saved to {filepath}")
    except IOError as e:
        print(f"Error saving data to {filepath}: {e}")


def load_json_from_file(filepath: str) -> Optional[Dict]:
    """
    Load JSON data from a file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Loaded dictionary or None if error occurs
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading data from {filepath}: {e}")
        return None

