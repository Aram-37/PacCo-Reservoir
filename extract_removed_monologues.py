#!/usr/bin/env python3
"""
Extract Removed Monologues
This script will re-process the original panacea files to extract the monologue content
that was removed during cleaning, and save it to a separate file for analysis.
"""

import re
import os
import glob
from datetime import datetime

def analyze_dialogue_section(section_content):
    """
    Analyze a dialogue section to extract speakers and content
    Returns: (speaker_count, speakers_list, is_monologue, content)
    """
    lines = section_content.split('\n')
    speakers = set()
    dialogue_lines = []
    
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
            dialogue_lines.append(line)
        elif line.startswith('- AI:') or line.startswith('- Assistant:'):
            speakers.add('AI')
            dialogue_lines.append(line)
        elif line.startswith('- ChatGPT:') or 'ChatGPT said:' in line:
            speakers.add('ChatGPT')
            dialogue_lines.append(line)
        elif line.startswith('- ') and ':' in line:
            # Extract speaker name from "- SpeakerName:"
            speaker_match = re.match(r'-\s*([^:]+):', line)
            if speaker_match:
                speaker_name = speaker_match.group(1).strip()
                speakers.add(speaker_name)
                dialogue_lines.append(line)
        else:
            # Non-dialogue content
            if line.strip():
                dialogue_lines.append(line)
    
    is_monologue = len(speakers) <= 1
    return len(speakers), list(speakers), is_monologue, dialogue_lines

def extract_monologues_from_file(file_path):
    """
    Extract monologue sections from a panacea file
    """
    monologues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return monologues
    
    # Split into sections based on the pattern ## Dialogues Section XXXXX
    sections = re.split(r'## Dialogues Section (\d+)', content)
    
    for i in range(1, len(sections), 2):
        section_num = sections[i]
        section_content = sections[i+1] if i+1 < len(sections) else ""
        
        speaker_count, speakers, is_monologue, dialogue_lines = analyze_dialogue_section(section_content)
        
        if is_monologue and dialogue_lines:
            # Clean up the content
            cleaned_content = []
            for line in dialogue_lines:
                if line.strip() and not line.startswith('[Content removed'):
                    cleaned_content.append(line)
            
            if cleaned_content:
                monologue_data = {
                    'file': os.path.basename(file_path),
                    'section': section_num,
                    'speakers': speakers,
                    'line_count': len(cleaned_content),
                    'content': cleaned_content,
                    'preview': ' '.join(cleaned_content[:3])[:200] + "..." if len(cleaned_content) > 3 else ' '.join(cleaned_content)
                }
                monologues.append(monologue_data)
    
    return monologues

def main():
    """
    Extract all monologues from panacea files and save to a new file
    """
    print("🔍 EXTRACTING REMOVED MONOLOGUES")
    print("=" * 60)
    
    # Find all panacea files
    panacea_files = glob.glob("panacea/panacea_*.md")
    panacea_files.sort()
    
    all_monologues = []
    file_stats = {}
    
    for file_path in panacea_files:
        print(f"Processing {file_path}...")
        monologues = extract_monologues_from_file(file_path)
        all_monologues.extend(monologues)
        file_stats[file_path] = len(monologues)
        print(f"  Found {len(monologues)} monologue sections")
    
    print(f"\n📊 EXTRACTION SUMMARY:")
    print(f"Total files processed: {len(panacea_files)}")
    print(f"Total monologues found: {len(all_monologues)}")
    
    # Create output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"extracted_monologues_{timestamp}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Extracted Monologues from Panacea Files\n\n")
        f.write(f"Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Monologues: {len(all_monologues)}\n\n")
        
        f.write("## Summary by File\n\n")
        for file_path, count in file_stats.items():
            f.write(f"- {file_path}: {count} monologues\n")
        
        f.write("\n## Speaker Distribution\n\n")
        speaker_counts = {}
        for mono in all_monologues:
            for speaker in mono['speakers']:
                speaker_counts[speaker] = speaker_counts.get(speaker, 0) + 1
        
        for speaker, count in sorted(speaker_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- {speaker}: {count} sections\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("## MONOLOGUE CONTENT\n")
        f.write("="*80 + "\n\n")
        
        # Group by file for better organization
        current_file = None
        for mono in all_monologues:
            if mono['file'] != current_file:
                current_file = mono['file']
                f.write(f"\n### File: {current_file}\n\n")
            
            f.write(f"#### Section {mono['section']}\n")
            f.write(f"**Speakers:** {', '.join(mono['speakers']) if mono['speakers'] else 'None detected'}\n")
            f.write(f"**Lines:** {mono['line_count']}\n")
            f.write(f"**Preview:** {mono['preview']}\n\n")
            f.write("**Full Content:**\n")
            f.write("```\n")
            for line in mono['content']:
                f.write(f"{line}\n")
            f.write("```\n\n")
            f.write("---\n\n")
    
    print(f"\n✅ EXTRACTION COMPLETE!")
    print(f"Monologues saved to: {output_file}")
    print(f"Total sections extracted: {len(all_monologues)}")
    
    # Show some sample content
    if all_monologues:
        print(f"\n📋 SAMPLE MONOLOGUE PREVIEW:")
        print("=" * 40)
        sample = all_monologues[0]
        print(f"File: {sample['file']}")
        print(f"Section: {sample['section']}")
        print(f"Speakers: {sample['speakers']}")
        print(f"Preview: {sample['preview'][:150]}...")
        
        if len(all_monologues) > 1:
            print("\n" + "=" * 40)
            sample2 = all_monologues[min(10, len(all_monologues)-1)]
            print(f"File: {sample2['file']}")
            print(f"Section: {sample2['section']}")
            print(f"Speakers: {sample2['speakers']}")
            print(f"Preview: {sample2['preview'][:150]}...")

if __name__ == "__main__":
    main()
