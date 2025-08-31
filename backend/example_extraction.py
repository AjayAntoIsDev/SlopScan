"""
Example usage of the Tree-sitter code extractor for AI code detection.
This script demonstrates how to extract code features for analysis.
"""

import asyncio
import json
from app.services.code_extractor import TreeSitterExtractor, extract_code_features, extract_features_from_file

# Example Python code to analyze
EXAMPLE_PYTHON_CODE = '''
"""
Example Python module for demonstration.
This module contains various code patterns for feature extraction.
"""

import os
import sys
from typing import List, Dict, Any
import requests

# Global constants
API_BASE_URL = "https://api.example.com"
MAX_RETRIES = 3

class DataProcessor:
    """A class for processing data."""
    
    def __init__(self, config_file: str):
        """Initialize the data processor."""
        self.config_file = config_file
        self.data = []
    
    def load_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Load data from a file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return []
    
    def process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single data item."""
        # TODO: Implement actual processing logic
        processed = {
            'id': item.get('id', ''),
            'value': item.get('value', 0) * 2,
            'status': 'processed'
        }
        return processed
    
    def fetch_remote_data(self, endpoint: str) -> Dict[str, Any]:
        """Fetch data from remote API."""
        url = f"{API_BASE_URL}/{endpoint}"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Failed to fetch data: {e}")
            return {}

def main():
    """Main function."""
    processor = DataProcessor("config.json")
    
    # Process local data
    local_data = processor.load_data("input.json")
    for item in local_data:
        result = processor.process_item(item)
        print(f"Processed: {result}")
    
    # Fetch remote data
    remote_data = processor.fetch_remote_data("users")
    print(f"Remote data: {remote_data}")

if __name__ == "__main__":
    main()
'''

EXAMPLE_JAVASCRIPT_CODE = '''
/**
 * Example JavaScript module for feature extraction demonstration.
 * This shows various JS patterns and constructs.
 */

const API_BASE = 'https://api.example.com';
const MAX_ITEMS = 100;

// Import statements
import axios from 'axios';
import { debounce, throttle } from 'lodash';

class UserManager {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.users = [];
        this.cache = new Map();
    }
    
    /**
     * Fetch users from the API
     * @param {number} limit - Maximum number of users to fetch
     * @returns {Promise<Array>} Array of user objects
     */
    async fetchUsers(limit = 10) {
        try {
            const response = await axios.get(`${API_BASE}/users`, {
                params: { limit },
                headers: { 'Authorization': `Bearer ${this.apiKey}` }
            });
            return response.data;
        } catch (error) {
            console.error('Failed to fetch users:', error.message);
            return [];
        }
    }
    
    filterActiveUsers(users) {
        return users.filter(user => user.active && user.lastLogin);
    }
    
    // Arrow function example
    validateUser = (user) => {
        const requiredFields = ['id', 'email', 'name'];
        return requiredFields.every(field => user[field]);
    }
}

// Function declaration
function processUserData(rawData) {
    const processed = rawData.map(item => ({
        id: item.user_id,
        name: item.full_name || 'Unknown',
        email: item.email_address,
        status: item.is_active ? 'active' : 'inactive'
    }));
    
    return processed;
}

// Export
export { UserManager, processUserData };
'''

async def demonstrate_extraction():
    """Demonstrate code feature extraction."""
    
    print("=== Tree-sitter Code Feature Extraction Demo ===\n")
    
    # Initialize extractor
    extractor = TreeSitterExtractor()
    
    print("Supported languages:", extractor.get_supported_languages())
    print()
    
    # Extract Python features
    print("1. Extracting features from Python code:")
    print("-" * 40)
    
    python_features = extract_code_features(EXAMPLE_PYTHON_CODE, 'python', 'example.py')
    
    print(f"Strings found: {len(python_features.strings)}")
    for string in python_features.strings[:5]:  # Show first 5
        print(f"  - {string}")
    
    print(f"\nFunction names: {python_features.function_names}")
    print(f"Class names: {python_features.class_names}")
    print(f"Variable names (first 10): {python_features.variable_names[:10]}")
    print(f"Imports: {python_features.imports}")
    print(f"Comments found: {len(python_features.comments)}")
    print(f"Docstrings found: {len(python_features.docstrings)}")
    
    if python_features.docstrings:
        print("\nFirst docstring:")
        print(f"  {python_features.docstrings[0][:100]}...")
    
    print("\n" + "="*60 + "\n")
    
    # Extract JavaScript features
    print("2. Extracting features from JavaScript code:")
    print("-" * 40)
    
    js_features = extract_code_features(EXAMPLE_JAVASCRIPT_CODE, 'javascript', 'example.js')
    
    print(f"Strings found: {len(js_features.strings)}")
    for string in js_features.strings[:5]:
        print(f"  - {string}")
    
    print(f"\nFunction names: {js_features.function_names}")
    print(f"Class names: {js_features.class_names}")
    print(f"Method names: {js_features.method_names}")
    print(f"Variable names (first 10): {js_features.variable_names[:10]}")
    print(f"Imports: {js_features.imports}")
    print(f"Comments found: {len(js_features.comments)}")
    
    print("\n" + "="*60 + "\n")
    
    # Show feature comparison for AI analysis
    print("3. Feature comparison for AI analysis:")
    print("-" * 40)
    
    print("Python vs JavaScript feature comparison:")
    print(f"  Python - Functions: {len(python_features.function_names)}, Classes: {len(python_features.class_names)}")
    print(f"  JavaScript - Functions: {len(js_features.function_names)}, Classes: {len(js_features.class_names)}")
    
    print(f"\n  Python imports: {len(python_features.imports)}")
    print(f"  JavaScript imports: {len(js_features.imports)}")
    
    print(f"\n  Python strings: {len(python_features.strings)}")
    print(f"  JavaScript strings: {len(js_features.strings)}")
    
    # Example of how to use features for similarity detection
    print("\n4. Features for similarity detection:")
    print("-" * 40)
    
    def get_feature_signature(features):
        """Generate a simple signature for similarity comparison."""
        return {
            'function_count': len(features.function_names),
            'class_count': len(features.class_names),
            'string_count': len(features.strings),
            'import_count': len(features.imports),
            'variable_count': len(features.variable_names),
            'comment_count': len(features.comments),
            'language': features.language
        }
    
    python_sig = get_feature_signature(python_features)
    js_sig = get_feature_signature(js_features)
    
    print("Python signature:", json.dumps(python_sig, indent=2))
    print("\nJavaScript signature:", json.dumps(js_sig, indent=2))
    
    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    asyncio.run(demonstrate_extraction())
