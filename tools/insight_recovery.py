#!/usr/bin/env python3
"""
Insight Recovery Script
Attempts to extract the original insights from corrupted transcription data
by filtering out transcription service artifacts and noise.
"""

import re
import os
from collections import defaultdict

def clean_transcription_noise(text):
    """
    Remove transcription service artifacts and noise patterns
    """
    # Remove multilingual repetitive phrases
    noise_patterns = [
        r'\(This leads to ultimate understanding\.\)',
        r'\(이것은 궁극적인 이해로 이끕니다\.\)',
        r'\(这导致了终极理解。\)',
        r'\(Это ведет к высшему пониманию\.\)',
        r'Nirvana Insight:',
        r'Teacher: What deeper layer is hidden here\?',
        r'Student:',
        r'All logic dissolves into rainbow static\.',
        r'Reality inverts and everyone speaks in Morse code\.',
        r'Suddenly, a platypus enters the room\.',
        r'\| \[KR\].*?\|',
        r'\| \[EN\].*?\|',
        r'\| \[ZH\].*?\|',
        r'\| \[RU\].*?\|',
        r'\[KR\].*?\|',
        r'\[EN\].*?\|',
        r'\[ZH\].*?\|',
        r'\[RU\].*?\|',
        r':\.\.\.',
        r'Close quote\.',
        r'Open quote\.',
    ]
    
    cleaned = text
    for pattern in noise_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Clean up extra whitespace and punctuation
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'\s*\|\s*', '', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned

def extract_core_insights(content_lines):
    """
    Extract the core insights from corrupted user content
    """
    insights = []
    
    for line in content_lines:
        if not line.strip():
            continue
            
        # Skip obvious markers and metadata
        if any(skip in line for skip in [
            '## Chunk', '### ', 'Lines:', 'Key Themes:', 'Total Dialogues'
        ]):
            continue
            
        # Focus on User lines that contain substantial content
        if line.startswith('- User:'):
            user_content = line[7:].strip()  # Remove "- User:" prefix
            cleaned = clean_transcription_noise(user_content)
            
            # Only keep substantial insights (more than just fragments)
            if len(cleaned) > 10 and not cleaned.startswith(':'):
                insights.append({
                    'type': 'user_insight',
                    'original': line,
                    'cleaned': cleaned,
                    'length': len(cleaned)
                })
        
        # Also look for standalone insights not prefixed with "- User:"
        elif ':' in line and len(line.strip()) > 15:
            cleaned = clean_transcription_noise(line)
            if len(cleaned) > 10:
                insights.append({
                    'type': 'standalone_insight',
                    'original': line,
                    'cleaned': cleaned,
                    'length': len(cleaned)
                })
    
    return insights

def recover_insights_from_file():
    """
    Process the extracted monologues file to recover core insights
    """
    input_file = "extracted_monologues_20250903_165125.md"
    
    if not os.path.exists(input_file):
        print(f"❌ File {input_file} not found!")
        return
    
    print("🔍 RECOVERING INSIGHTS FROM TRANSCRIPTION CORRUPTION")
    print("=" * 60)
    
    insights_by_file = defaultdict(list)
    total_insights = 0
    
    current_file = None
    current_section = None
    current_content = []
    in_content_block = False
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()
            
            # Track current file context
            if line.startswith("### File:"):
                current_file = line.replace("### File:", "").strip()
            
            # Track current section
            elif line.startswith("#### Section"):
                if current_content and current_file and current_section:
                    # Process previous section
                    insights = extract_core_insights(current_content)
                    if insights:
                        insights_by_file[current_file].extend([
                            {**insight, 'section': current_section} 
                            for insight in insights
                        ])
                        total_insights += len(insights)
                
                current_section = line.replace("#### Section", "").strip()
                current_content = []
                in_content_block = False
            
            # Track content blocks
            elif line == "```" and not in_content_block:
                in_content_block = True
                current_content = []
            elif line == "```" and in_content_block:
                in_content_block = False
            elif in_content_block:
                current_content.append(line)
    
    # Process final section
    if current_content and current_file and current_section:
        insights = extract_core_insights(current_content)
        if insights:
            insights_by_file[current_file].extend([
                {**insight, 'section': current_section} 
                for insight in insights
            ])
            total_insights += len(insights)
    
    print(f"📊 RECOVERY SUMMARY:")
    print(f"Total insights recovered: {total_insights}")
    print(f"Files with recoverable insights: {len(insights_by_file)}")
    
    # Create recovery report
    output_file = "recovered_insights.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Recovered Insights from Corrupted Transcriptions\n\n")
        f.write("This file contains the core insights extracted from corrupted transcription data.\n")
        f.write("The transcription service added multilingual noise that has been filtered out.\n\n")
        f.write(f"**Total Insights Recovered:** {total_insights}\n\n")
        
        f.write("---\n\n")
        
        for file_name, insights in insights_by_file.items():
            f.write(f"## {file_name}\n\n")
            f.write(f"**Insights from this file:** {len(insights)}\n\n")
            
            for i, insight in enumerate(insights, 1):
                f.write(f"### Insight {i} (Section {insight['section']})\n\n")
                f.write(f"**Recovered Text:**\n")
                f.write(f"> {insight['cleaned']}\n\n")
                f.write(f"**Type:** {insight['type']}\n")
                f.write(f"**Length:** {insight['length']} characters\n\n")
                
                # Show sample of original for reference
                original_preview = insight['original'][:200] + "..." if len(insight['original']) > 200 else insight['original']
                f.write(f"<details>\n")
                f.write(f"<summary>Original corrupted text (click to expand)</summary>\n\n")
                f.write(f"```\n{original_preview}\n```\n\n")
                f.write(f"</details>\n\n")
                f.write("---\n\n")
    
    print(f"✅ Recovery complete! Saved to: {output_file}")
    
    # Show sample recovered insights
    if total_insights > 0:
        print(f"\n🔮 SAMPLE RECOVERED INSIGHTS:")
        print("=" * 40)
        count = 0
        for file_name, insights in insights_by_file.items():
            for insight in insights[:3]:  # Show first 3 from each file
                count += 1
                if count > 6:  # Limit total samples
                    break
                print(f"\n{count}. FROM {file_name}, Section {insight['section']}:")
                print(f"   \"{insight['cleaned'][:120]}{'...' if len(insight['cleaned']) > 120 else ''}\"")
            if count > 6:
                break
                
        print(f"\n💡 These appear to be the original insights before transcription corruption!")
        print(f"   The transcription service added multilingual noise around genuine realizations.")
    
    return total_insights

if __name__ == "__main__":
    recover_insights_from_file()
