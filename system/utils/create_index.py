#!/usr/bin/env python3
"""
Index Creation Tool for AI Research Environment

This script generates a comprehensive index of the research environment structure,
documenting all scripts, configurations, and documentation files.
"""

import os
import json
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Define default project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Categories for file classification
FILE_CATEGORIES = {
    'python': ['.py', '.ipynb'],
    'docker': ['Dockerfile', '.dockerignore', 'docker-compose.yml', '.yml', '.yaml'],
    'script': ['.sh', '.bash'],
    'documentation': ['.md', '.txt', '.rst'],
    'data': ['.csv', '.json', '.npy', '.npz', '.h5', '.hdf5', '.parquet'],
    'configuration': ['.ini', '.cfg', '.conf', '.json', '.env'],
    'other': []
}

# Directories to exclude
EXCLUDE_DIRS = [
    '.git', '__pycache__', '.ipynb_checkpoints', 'venv', 'env',
    'node_modules', '.pytest_cache'
]

def categorize_file(filename: str) -> str:
    """Determine the category of a file based on its extension."""
    ext = os.path.splitext(filename)[1].lower()
    basename = os.path.basename(filename)
    
    # Special case for known files without extensions
    if basename in ['Dockerfile', 'docker-compose.yml', 'Makefile']:
        return 'docker' if 'docker' in basename.lower() else 'configuration'
    
    # Categorize by extension
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions or basename in extensions:
            return category
    
    return 'other'

def scan_directory(base_path: Path) -> Dict:
    """Scan directory and categorize all files."""
    all_files = []
    by_category = {}
    
    for root, dirs, files in os.walk(base_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        root_path = Path(root)
        rel_path = root_path.relative_to(base_path)
        
        for file in files:
            if file in EXCLUDE_DIRS:
                continue
                
            file_path = root_path / file
            if not file_path.is_file():
                continue
                
            rel_file_path = rel_path / file
            str_path = str(rel_file_path).replace('\\', '/')
            
            category = categorize_file(file)
            
            file_info = {
                'path': str_path,
                'category': category,
                'size': file_path.stat().st_size,
                'modified': datetime.datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            
            all_files.append(file_info)
            
            if category not in by_category:
                by_category[category] = []
                
            by_category[category].append(file_info)
    
    return {
        'all_files': all_files,
        'by_category': by_category,
        'statistics': {
            'total_files': len(all_files),
            'categories': {cat: len(files) for cat, files in by_category.items()}
        }
    }

def create_markdown_index(index_data: Dict, output_file: Path) -> None:
    """Generate a markdown index of files."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# AI Research Environment Index\n\n")
        f.write(f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Write summary
        f.write("## Summary\n\n")
        f.write(f"Total files: {index_data['statistics']['total_files']}\n\n")
        
        f.write("| Category | Count |\n")
        f.write("|----------|-------|\n")
        for category, count in sorted(index_data['statistics']['categories'].items()):
            f.write(f"| {category.capitalize()} | {count} |\n")
        
        f.write("\n\n")
        
        # Write files by category
        for category, files in sorted(index_data['by_category'].items()):
            f.write(f"## {category.capitalize()} Files\n\n")
            
            f.write("| File | Size | Last Modified |\n")
            f.write("|------|------|---------------|\n")
            
            for file_info in sorted(files, key=lambda x: x['path']):
                size_kb = file_info['size'] / 1024
                date = file_info['modified'].split('T')[0]
                f.write(f"| [{file_info['path']}]({file_info['path']}) | {size_kb:.1f} KB | {date} |\n")
            
            f.write("\n")

def create_json_index(index_data: Dict, output_file: Path) -> None:
    """Generate a JSON index of files."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2)

def main() -> None:
    """Main function to generate index files."""
    parser = argparse.ArgumentParser(description='Generate index of research environment files')
    parser.add_argument('--base-dir', type=str, default=str(PROJECT_ROOT),
                      help='Base directory to scan (default: project root)')
    parser.add_argument('--output-dir', type=str, default=str(PROJECT_ROOT),
                      help='Output directory for index files (default: project root)')
    parser.add_argument('--format', choices=['md', 'json', 'both'], default='both',
                      help='Output format (default: both markdown and JSON)')
    args = parser.parse_args()
    
    base_dir = Path(args.base_dir)
    output_dir = Path(args.output_dir)
    
    print(f"Scanning directory: {base_dir}")
    index_data = scan_directory(base_dir)
    
    if args.format in ['md', 'both']:
        md_file = output_dir / 'index.md'
        create_markdown_index(index_data, md_file)
        print(f"Created Markdown index: {md_file}")
    
    if args.format in ['json', 'both']:
        json_file = output_dir / 'file_index.json'
        create_json_index(index_data, json_file)
        print(f"Created JSON index: {json_file}")
    
    print(f"Indexing complete! Found {index_data['statistics']['total_files']} files.")

if __name__ == "__main__":
    main()
