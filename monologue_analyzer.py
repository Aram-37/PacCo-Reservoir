#!/usr/bin/env python3
"""
Monologue Pattern Analyzer
Extracts and analyzes patterns in single-entity dialogue sections
"""

import re
import os
import glob
from collections import Counter, defaultdict

def analyze_dialogue_section(section_content):
    """
    Analyze a dialogue section to extract speakers and content
    """
    lines = section_content.split('\n')
    speakers = set()
    dialogue_lines = []
    content_by_speaker = defaultdict(list)
    
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
            content = line[7:].strip()  # Remove "- User:" prefix
            dialogue_lines.append(('User', content))
            content_by_speaker['User'].append(content)
        elif line.startswith('- AI:') or line.startswith('- Assistant:'):
            speakers.add('AI')
            content = line[line.index(':')+1:].strip()
            dialogue_lines.append(('AI', content))
            content_by_speaker['AI'].append(content)
        elif line.startswith('- ChatGPT:') or 'ChatGPT said:' in line:
            speakers.add('ChatGPT')
            if 'ChatGPT said:' in line:
                content = line.split('ChatGPT said:', 1)[1].strip()
            else:
                content = line[10:].strip()  # Remove "- ChatGPT:" prefix
            dialogue_lines.append(('ChatGPT', content))
            content_by_speaker['ChatGPT'].append(content)
        elif line.startswith('- ') and ':' in line:
            # Extract speaker name from "- SpeakerName:"
            speaker_match = re.match(r'-\s*([^:]+):', line)
            if speaker_match:
                speaker_name = speaker_match.group(1).strip()
                speakers.add(speaker_name)
                content = line.split(':', 1)[1].strip()
                dialogue_lines.append((speaker_name, content))
                content_by_speaker[speaker_name].append(content)
        elif ':' in line and ('said:' in line or 'asked:' in line):
            # Handle "SpeakerName said:" patterns
            speaker_match = re.match(r'([^:]+)\s+(?:said|asked):', line)
            if speaker_match:
                speaker_name = speaker_match.group(1).strip()
                speakers.add(speaker_name)
                content = line.split(':', 1)[1].strip()
                dialogue_lines.append((speaker_name, content))
                content_by_speaker[speaker_name].append(content)
    
    return len(speakers), dialogue_lines, content_by_speaker

def extract_monologue_patterns(file_path):
    """
    Extract monologue patterns from a file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all dialogue sections
        sections = re.split(r'(## Dialogues Section \d+:.*?)(?=\n## Dialogues Section|\n## [^D]|\Z)', content, flags=re.DOTALL)
        
        monologues = []
        
        for section in sections:
            if section.startswith('## Dialogues Section'):
                speaker_count, dialogue_lines, content_by_speaker = analyze_dialogue_section(section)
                
                if speaker_count == 1 and len(dialogue_lines) > 0:
                    # Extract section number
                    section_match = re.search(r'## Dialogues Section (\d+):', section)
                    section_num = section_match.group(1) if section_match else "unknown"
                    
                    # Get the single speaker
                    speaker = list(content_by_speaker.keys())[0]
                    
                    monologue_data = {
                        'section_num': section_num,
                        'speaker': speaker,
                        'line_count': len(dialogue_lines),
                        'content': content_by_speaker[speaker],
                        'raw_section': section
                    }
                    monologues.append(monologue_data)
        
        return monologues
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {str(e)}")
        return []

def analyze_content_patterns(monologues):
    """
    Analyze patterns in monologue content
    """
    patterns = {
        'word_frequency': Counter(),
        'phrase_patterns': Counter(),
        'content_lengths': [],
        'common_themes': Counter(),
        'speaker_stats': Counter(),
        'examples_by_pattern': defaultdict(list)
    }
    
    for mono in monologues:
        speaker = mono['speaker']
        patterns['speaker_stats'][speaker] += 1
        
        for content in mono['content']:
            # Word frequency
            words = re.findall(r'\b\w+\b', content.lower())
            patterns['word_frequency'].update(words)
            
            # Content length
            patterns['content_lengths'].append(len(content))
            
            # Look for common patterns
            content_lower = content.lower()
            
            # Detect themes/patterns
            if any(word in content_lower for word in ['i think', 'i believe', 'i feel']):
                patterns['common_themes']['personal_opinion'] += 1
                patterns['examples_by_pattern']['personal_opinion'].append(content[:100] + "...")
                
            if any(word in content_lower for word in ['question', 'ask', 'wonder']):
                patterns['common_themes']['questioning'] += 1
                patterns['examples_by_pattern']['questioning'].append(content[:100] + "...")
                
            if any(word in content_lower for word in ['because', 'since', 'due to']):
                patterns['common_themes']['explanatory'] += 1
                patterns['examples_by_pattern']['explanatory'].append(content[:100] + "...")
                
            if any(word in content_lower for word in ['but', 'however', 'although']):
                patterns['common_themes']['contrasting'] += 1
                patterns['examples_by_pattern']['contrasting'].append(content[:100] + "...")
                
            if any(word in content_lower for word in ['you', 'your', 'yourself']):
                patterns['common_themes']['addressing_ai'] += 1
                patterns['examples_by_pattern']['addressing_ai'].append(content[:100] + "...")
                
            if re.search(r'\b(?:should|must|need|have to)\b', content_lower):
                patterns['common_themes']['directive'] += 1
                patterns['examples_by_pattern']['directive'].append(content[:100] + "...")
    
    return patterns

def main():
    """
    Analyze monologue patterns across all panacea files
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    panacea_dir = os.path.join(current_dir, 'panacea')
    
    if os.path.exists(panacea_dir):
        panacea_files = glob.glob(os.path.join(panacea_dir, "*.md"))
    else:
        panacea_files = glob.glob(os.path.join(current_dir, "panacea*.md"))
    
    all_monologues = []
    
    print("🔍 Extracting monologue patterns...")
    print("=" * 60)
    
    for file_path in sorted(panacea_files):
        filename = os.path.basename(file_path)
        monologues = extract_monologue_patterns(file_path)
        
        if monologues:
            print(f"📝 {filename}: {len(monologues)} monologue sections found")
            all_monologues.extend(monologues)
        else:
            print(f"✅ {filename}: No monologue sections")
    
    if all_monologues:
        print("\n" + "=" * 60)
        print("📊 MONOLOGUE PATTERN ANALYSIS")
        print("=" * 60)
        
        patterns = analyze_content_patterns(all_monologues)
        
        print(f"\n🎭 SPEAKER BREAKDOWN:")
        for speaker, count in patterns['speaker_stats'].most_common():
            print(f"  {speaker}: {count} monologue sections")
        
        print(f"\n📏 CONTENT LENGTH STATS:")
        lengths = patterns['content_lengths']
        if lengths:
            print(f"  Average content length: {sum(lengths) / len(lengths):.1f} characters")
            print(f"  Shortest: {min(lengths)} characters")
            print(f"  Longest: {max(lengths)} characters")
        
        print(f"\n🎯 COMMON THEMES:")
        for theme, count in patterns['common_themes'].most_common():
            print(f"  {theme}: {count} occurrences")
        
        print(f"\n📝 TOP WORDS:")
        # Filter out common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'can', 'may', 'might', 'must', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        filtered_words = [(word, count) for word, count in patterns['word_frequency'].most_common(20) 
                         if word not in common_words and len(word) > 2]
        
        for word, count in filtered_words[:15]:
            print(f"  '{word}': {count} times")
        
        print(f"\n💡 EXAMPLE CONTENT BY PATTERN:")
        for pattern_name, examples in patterns['examples_by_pattern'].items():
            if examples:
                print(f"\n  {pattern_name.upper()}:")
                for i, example in enumerate(examples[:3]):  # Show first 3 examples
                    print(f"    {i+1}. {example}")
        
        print("\n" + "=" * 60)
        print(f"📈 TOTAL MONOLOGUES ANALYZED: {len(all_monologues)}")
        
        # Save detailed analysis to file
        output_file = os.path.join(current_dir, "monologue_analysis.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("DETAILED MONOLOGUE ANALYSIS\n")
            f.write("=" * 50 + "\n\n")
            
            for i, mono in enumerate(all_monologues[:20]):  # First 20 examples
                f.write(f"EXAMPLE {i+1}:\n")
                f.write(f"Section: {mono['section_num']}\n")
                f.write(f"Speaker: {mono['speaker']}\n")
                f.write(f"Lines: {mono['line_count']}\n")
                f.write("Content:\n")
                for j, content in enumerate(mono['content'][:3]):  # First 3 lines
                    f.write(f"  {j+1}. {content}\n")
                f.write("\n" + "-" * 30 + "\n\n")
        
        print(f"💾 Detailed analysis saved to: {output_file}")
    
    else:
        print("\n✅ No monologues found in any files!")

if __name__ == "__main__":
    main()
