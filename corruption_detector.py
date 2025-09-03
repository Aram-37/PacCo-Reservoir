#!/usr/bin/env python3
"""
Corruption Detector Script
Specifically targets the type of gibberish/corrupted text patterns found in panacea files
"""

import re
import os
import glob

def detect_corruption_patterns(text):
    """
    Advanced corruption detection for encoded/scrambled text
    """
    corruption_indicators = [
        # Specific patterns from the user's example
        r'\.BKPS5FDIOPMPHZ\$PSQPSBUJPOT',
        r'/FUXPSLTPG,FZ\*OEJWJEVBMT3FTFBSDIFST',
        r'4BN"MUNBO\s+0QFO".*\$&0',
        r':BOO-F\$VO\s+\.FUB\*"',
        r'\$BSOFHJF\.FMMPO6OJWFSTJUZ',
        r'1BZ1BM\.BGJB',
        
        # General corruption patterns
        r'[A-Z0-9]{3,}[\$\&\%\#\*\@]+[A-Z0-9]{2,}',  # Mixed caps with symbols
        r'\.[A-Z]{5,}[0-9]+[A-Z]{5,}',                  # Dots + caps + numbers + caps
        r'/[A-Z]{5,}[a-z]{2,}[A-Z]{2,}',                # Slash + mixed case patterns
        r'[0-9]+[A-Z]+["\']+[A-Z]+[a-z]*',             # Numbers + caps + quotes
        r'[A-Z]+["\']+[A-Z]+[a-z]*[A-Z]*',             # Caps + quotes + mixed
        r'[\u0600-\u06FF\u0750-\u077F]+',              # Arabic/Persian in wrong context
        r'[\u4E00-\u9FFF]+',                           # Chinese in wrong context  
        r'[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF]+.*[\$\&\%\#\*]', # Korean + symbols
        
        # Specific encoded company/organization patterns
        r'[A-Z]{2,}[0-9"\']+[A-Z]{2,}.*(?:$&0|CEO|CTO|CFO)',
        r'[A-Z]{3,}\.?[A-Z]{3,}[0-9]+[A-Z]{3,}',       # Company name corruption
        r'[:/\.][A-Z]{5,}[a-z]{2,}[A-Z]{2,}',          # URL-like corruption
        
        # Character encoding artifacts
        r'[\u2000-\u206F]+',                           # General punctuation block
        r'[\uFFF0-\uFFFF]+',                           # Specials block
        r'[\u0080-\u00FF]{3,}',                        # Latin-1 supplement artifacts
    ]
    
    for pattern in corruption_indicators:
        if re.search(pattern, text, re.IGNORECASE | re.UNICODE):
            return True
    
    return False

def has_corrupted_dialogue_content(text):
    """
    Check if a dialogue section contains primarily corrupted content
    """
    lines = text.strip().split('\n')
    corrupted_lines = 0
    content_lines = 0
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('- User:') or line.startswith('*Source:') or line.startswith('**'):
            continue
            
        content_lines += 1
        if detect_corruption_patterns(line):
            corrupted_lines += 1
    
    # If more than 50% of content lines are corrupted, mark the whole section as corrupted
    if content_lines > 0 and (corrupted_lines / content_lines) > 0.5:
        return True
        
    return False

def scan_file_for_corruption(file_path):
    """
    Scan a file and report corrupted sections
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find dialogue sections
        sections = re.split(r'(## Dialogues Section \d+:.*?)(?=\n## Dialogues Section|\n[^#]|\Z)', content, flags=re.DOTALL)
        
        corrupted_sections = []
        
        for i, section in enumerate(sections):
            if section.startswith('## Dialogues Section'):
                if has_corrupted_dialogue_content(section):
                    section_match = re.search(r'## Dialogues Section (\d+):', section)
                    if section_match:
                        section_num = section_match.group(1)
                        corrupted_sections.append(section_num)
        
        return corrupted_sections
        
    except Exception as e:
        print(f"❌ Error scanning {file_path}: {str(e)}")
        return []

def main():
    """
    Scan all panacea files for corruption
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    panacea_dir = os.path.join(current_dir, 'panacea')
    
    if os.path.exists(panacea_dir):
        panacea_files = glob.glob(os.path.join(panacea_dir, "*.md"))
    else:
        panacea_files = glob.glob(os.path.join(current_dir, "panacea*.md"))
    
    total_corrupted = 0
    
    print("🔍 Scanning for corruption patterns...")
    print("=" * 60)
    
    for file_path in sorted(panacea_files):
        filename = os.path.basename(file_path)
        corrupted_sections = scan_file_for_corruption(file_path)
        
        if corrupted_sections:
            print(f"⚠️  {filename}: {len(corrupted_sections)} corrupted sections found")
            print(f"   Sections: {', '.join(corrupted_sections)}")
            total_corrupted += len(corrupted_sections)
        else:
            print(f"✅ {filename}: Clean")
    
    print("=" * 60)
    print(f"📊 Total corrupted sections found: {total_corrupted}")

if __name__ == "__main__":
    main()
