#!/usr/bin/env python3
"""
Single Entity Dialogue Cleaner
Removes dialogue sections where only one entity is speaking (no actual dialogue)
"""

import re
import os
import glob

def analyze_dialogue_section(section_content):
    """
    Analyze a dialogue section to count unique speakers
    """
    lines = section_content.split('\n')
    speakers = set()
    dialogue_lines = 0
    
    for line in lines:
        line = line.strip()
        
        # Skip headers, source lines, and empty lines
        if (not line or 
            line.startswith('## Dialogues Section') or 
            line.startswith('*Source:') or 
            line.startswith('**') or
            line.startswith('[Content removed') or
            line.startswith('# ') or
            line.startswith('---')):
            continue
        
        # Look for dialogue patterns
        if line.startswith('- User:'):
            speakers.add('User')
            dialogue_lines += 1
        elif line.startswith('- AI:') or line.startswith('- Assistant:'):
            speakers.add('AI')
            dialogue_lines += 1
        elif line.startswith('- ChatGPT:') or 'ChatGPT said:' in line:
            speakers.add('ChatGPT')
            dialogue_lines += 1
        elif line.startswith('- ') and ':' in line:
            # Extract speaker name from "- SpeakerName:"
            speaker_match = re.match(r'-\s*([^:]+):', line)
            if speaker_match:
                speaker_name = speaker_match.group(1).strip()
                speakers.add(speaker_name)
                dialogue_lines += 1
        elif ':' in line and ('said:' in line or 'asked:' in line):
            # Handle "SpeakerName said:" patterns
            speaker_match = re.match(r'([^:]+)\s+(?:said|asked):', line)
            if speaker_match:
                speaker_name = speaker_match.group(1).strip()
                speakers.add(speaker_name)
                dialogue_lines += 1
    
    return len(speakers), dialogue_lines, speakers

def is_single_entity_section(section_content):
    """
    Check if a dialogue section has only one entity speaking
    """
    speaker_count, dialogue_lines, speakers = analyze_dialogue_section(section_content)
    
    # If we have fewer than 2 speakers and at least some dialogue content, it's a single entity section
    if speaker_count < 2 and dialogue_lines > 0:
        return True, speakers, dialogue_lines
    
    return False, speakers, dialogue_lines

def clean_single_entity_sections(file_path):
    """
    Clean single entity dialogue sections from a file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all dialogue sections
        sections = re.split(r'(## Dialogues Section \d+:.*?)(?=\n## Dialogues Section|\n## [^D]|\Z)', content, flags=re.DOTALL)
        
        cleaned_sections = []
        single_entity_count = 0
        
        for section in sections:
            if section.startswith('## Dialogues Section'):
                is_single, speakers, dialogue_lines = is_single_entity_section(section)
                
                if is_single:
                    # Extract section number for reporting
                    section_match = re.search(r'## Dialogues Section (\d+):', section)
                    section_num = section_match.group(1) if section_match else "unknown"
                    
                    # Replace with placeholder
                    header_lines = []
                    for line in section.split('\n'):
                        if (line.startswith('## Dialogues Section') or 
                            line.startswith('*Source:') or 
                            line.startswith('**')):
                            header_lines.append(line)
                        else:
                            break
                    
                    cleaned_section = '\n'.join(header_lines) + '\n[Content removed - single entity monologue, not dialogue]\n'
                    cleaned_sections.append(cleaned_section)
                    single_entity_count += 1
                    
                    print(f"  Section {section_num}: Removed single entity ({list(speakers)}) with {dialogue_lines} lines")
                else:
                    cleaned_sections.append(section)
            else:
                cleaned_sections.append(section)
        
        if single_entity_count > 0:
            # Write back the cleaned content
            cleaned_content = ''.join(cleaned_sections)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            print(f"✅ Cleaned {os.path.basename(file_path)}: {single_entity_count} single entity sections removed")
            return single_entity_count
        else:
            print(f"ℹ️  {os.path.basename(file_path)}: No single entity sections found")
            return 0
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {str(e)}")
        return 0

def main():
    """
    Clean all panacea files to remove single entity dialogue sections
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    panacea_dir = os.path.join(current_dir, 'panacea')
    
    if os.path.exists(panacea_dir):
        panacea_files = glob.glob(os.path.join(panacea_dir, "*.md"))
    else:
        panacea_files = glob.glob(os.path.join(current_dir, "panacea*.md"))
    
    total_removed = 0
    
    print("🗣️  Analyzing dialogue sections for single entity monologues...")
    print("=" * 60)
    
    for file_path in sorted(panacea_files):
        removed_count = clean_single_entity_sections(file_path)
        total_removed += removed_count
    
    print("=" * 60)
    print(f"📊 Total single entity sections removed: {total_removed}")
    print("💡 Only keeping sections with actual dialogue between multiple entities")

if __name__ == "__main__":
    main()
