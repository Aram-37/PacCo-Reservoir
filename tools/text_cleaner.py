#!/usr/bin/env python3
"""
Advanced Text Cleaner Script
Removes lines containing specific technical terms and development-related content
from panacea files
"""

import re
import sys
import os
import glob
from pathlib import Path

def clean_chunk_excerpt(text):
    """
    Clean the chunk excerpt by removing lines containing technical terms
    """
    # Define words/patterns to filter out (comprehensive list)
    filter_words = [
        # TensorFlow and ML frameworks
        'tensor', 'tensorflow', 'pytorch', 'keras', 'sklearn',
        'pip_package', 'generate_lists', 'headers_list', 'srcs_list',
        
        # Development tools and environments
        'jovyan', 'kohya', 'jupyter', 'conda', 'venv', 'virtualenv',
        'dockerfile', 'requirements.txt', 'setup.py', 'pyproject.toml',
        
        # Git and version control
        'git commit', 'git add', 'git push', 'git pull', 'git clone',
        'create mode', 'insertions', 'deletions', 'master', 'main',
        'branch', 'merge', 'pull request', 'commit hash',
        
        # File paths and technical directories
        'tools/pip_package', '/usr/local/', '/opt/', '/home/',
        '../../../', '../../../../', 'node_modules', '__pycache__',
        
        # Programming and build terms
        'script', 'files changed', 'generate_lists.sh', 'makefile',
        'cmake', 'gcc', 'clang', 'compiler', 'linker', 'build',
        'npm install', 'yarn install', 'pip install',
        
        # Technical file extensions in context
        '.py:', '.js:', '.cpp:', '.h:', '.sh:', '.yml:', '.yaml:',
        '.json:', '.xml:', '.cfg:', '.ini:', '.conf:',
        
        # Database and server terms
        'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
        'apache', 'nginx', 'docker', 'kubernetes', 'aws', 'gcp',
        
        # Programming language specifics
        'import numpy', 'import pandas', 'import torch', 'import tensorflow',
        'from sklearn', 'import matplotlib', 'import seaborn',
        'def __init__', 'class ', 'function ', 'var ', 'let ', 'const ',
        
        # Terminal and system commands
        'sudo', 'chmod', 'chown', 'ls -la', 'cd ', 'mkdir', 'rm -rf',
        'curl', 'wget', 'ssh', 'scp', 'rsync',
        
        # Package managers and dependencies
        'package.json', 'yarn.lock', 'requirements.txt', 'poetry.lock',
        'pipfile', 'setup.cfg', 'tox.ini',
        
        # Corrupted/encoded text patterns
        'bkps5fdiopmphz', 'psqpsbujpot', 'fuxpsltpg', 'oejwjevbmt',
        '3ftfbsdifst', '4bn"nunbo', '0qfo"*', ':boo-f$vo', '.fub*"',
        '$bsofhjf.fmmpo6ojwfstjuz', '1bz1bm.bgjb',
        
        # Mixed character corruption patterns  
        'ࢳࣻҗ', 'ݴҗѢ', 'ࢳ', 'ࣻ', 'җ', 'ݴ', 'Ѣ'
    ]
    
    # Split text into lines
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Check if line contains any filter words (case insensitive)
        should_remove = False
        line_lower = line.lower()
        
        for word in filter_words:
            if word.lower() in line_lower:
                should_remove = True
                break
        
        # Additional pattern-based filtering
        patterns_to_remove = [
            r'jovyan@[\w-]+:',  # Terminal prompts
            r'\$\s+git\s+',     # Git commands
            r'create mode \d+', # Git file creation
            r'\d+ files? changed', # Git statistics
            r'\d+ insertions?\(\+\)', # Git insertions
            r'\d+ deletions?\(-\)',   # Git deletions
            r'^\s*[\w/]+\.sh\s+',     # Shell scripts
            r'^\s*\[[\w\s]+\]\s+',    # Git commit hashes
            r'../../../',             # Relative paths
            r'~~~~/',                 # Path separators
            r'^\s*\w+@\w+',          # Email-like patterns in dev context
            r'master\s+[a-f0-9]{7,}', # Git branch with hash
            r'HEAD\s+[a-f0-9]{7,}',   # Git HEAD references
            
            # Corrupted/encoded text patterns
            r'[A-Z0-9]{10,}[\$\*\&\%\#]+[A-Z0-9]+', # Mixed caps/numbers with symbols
            r'^[\.\#\$\&\%\*]+[A-Z0-9]+', # Starting with symbols + caps
            r'[0-9]+[A-Z]+[a-z]*[A-Z]+[0-9]*', # Number-caps-lower-caps-number patterns
            r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+', # Arabic/Persian scripts
            r'[\u4E00-\u9FFF\u3400-\u4DBF\u20000-\u2A6DF]+', # Chinese characters in wrong context
            r'[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF]+.*[A-Z0-9\$\&\%]+', # Korean + corrupted chars
            r'^[\.\/\$\&\%\#\*]+[A-Z]{3,}', # Symbols followed by caps
            r'[A-Z]{2,}[0-9]+[A-Z]{2,}[a-z]*[A-Z]*', # Caps-numbers-caps pattern
        ]
        
        for pattern in patterns_to_remove:
            if re.search(pattern, line, re.IGNORECASE):
                should_remove = True
                break
        
        # Keep lines that don't match filters and aren't empty
        if not should_remove and line.strip():
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def clean_file(file_path):
    """
    Clean a single file by removing technical content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content into chunks/sections
        sections = re.split(r'(\*\*Chunk Excerpt\*\*:.*?)(?=\n\n|\n\*\*|$)', content, flags=re.DOTALL)
        
        cleaned_sections = []
        changes_made = 0
        
        for section in sections:
            if section.startswith('**Chunk Excerpt**:'):
                # Extract the chunk content
                chunk_content = section[len('**Chunk Excerpt**:'):].strip()
                cleaned_chunk = clean_chunk_excerpt(chunk_content)
                
                if len(cleaned_chunk.strip()) == 0:
                    # Replace with placeholder if everything was removed
                    cleaned_sections.append('**Chunk Excerpt**: [Content removed - contained technical development logs]')
                    changes_made += 1
                elif len(cleaned_chunk) < len(chunk_content):
                    # Partial cleaning
                    cleaned_sections.append('**Chunk Excerpt**: ' + cleaned_chunk)
                    changes_made += 1
                else:
                    # No changes needed
                    cleaned_sections.append(section)
            else:
                cleaned_sections.append(section)
        
        if changes_made > 0:
            # Write back the cleaned content
            cleaned_content = ''.join(cleaned_sections)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            print(f"✅ Cleaned {file_path}: {changes_made} chunk(s) modified")
            return True
        else:
            print(f"ℹ️  No changes needed for {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {str(e)}")
        return False

def clean_all_panacea_files(directory_path):
    """
    Clean all panacea files in the specified directory
    """
    panacea_files = glob.glob(os.path.join(directory_path, "panacea*.md"))
    panacea_files.extend(glob.glob(os.path.join(directory_path, "cleaned_panacea*.md")))
    
    total_files = len(panacea_files)
    files_modified = 0
    
    print(f"🔍 Found {total_files} panacea files to process...")
    print("=" * 60)
    
    for file_path in sorted(panacea_files):
        if clean_file(file_path):
            files_modified += 1
    
    print("=" * 60)
    print(f"📊 Summary: {files_modified}/{total_files} files were modified")
    
    return files_modified

def main():
    """
    Main function - can clean a single chunk or all panacea files
    """
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        # Clean all panacea files
        current_dir = os.path.dirname(os.path.abspath(__file__))
        panacea_dir = os.path.join(current_dir, 'panacea')
        
        if os.path.exists(panacea_dir):
            clean_all_panacea_files(panacea_dir)
        else:
            # Try current directory
            clean_all_panacea_files(current_dir)
    else:
        # Demo with the original chunk excerpt
        chunk_text = """**Chunk Excerpt**: ../../../../generate_lists.sh ../../../tools/pip_package/headers_list.txt
../../../tools/pip_package/srcs_list.txt (118)
jovyan@kohya-0:~/tensorflow/tensorflow/tensorflow/tools/pip_package$ git commit -m "Add new script
and list files" [master ed46df74159] Add new script and list files 3 files changed, 20 insertions(+)
create mode 100644 generate_lists.sh create mode 100644
tensorflow/tools/pip_package/headers_list.txt create mode 100644
tensorflow/tools/pip_package/srcs_list.txt (118)
jovyan@ko..."""
        
        print("🧪 Demo: Original text:")
        print("-" * 50)
        print(chunk_text)
        print("\n" + "=" * 50 + "\n")
        
        cleaned_text = clean_chunk_excerpt(chunk_text)
        
        print("✨ Demo: Cleaned text:")
        print("-" * 50)
        print(cleaned_text if cleaned_text.strip() else "[All content removed - contained only filtered terms]")
        print("\n" + "=" * 50)
        print("💡 Tip: Use '--all' flag to clean all panacea files")
        print("   Example: python text_cleaner.py --all")

if __name__ == "__main__":
    main()
