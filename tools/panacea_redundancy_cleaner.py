#!/usr/bin/env python3
"""
Panacea Redundancy Cleaner
Removes redundant sentences and language codes from panacea files to reduce size.
"""

import os
import re
import json
from pathlib import Path

class PanaceaRedundancyCleaner:
    def __init__(self):
        # Get script directory and timestamp
        self.script_dir = Path(__file__).parent
        self.timestamp = str(Path(__file__).stat().st_mtime)
        
        # Common repeated phrases in multiple languages
        self.redundant_phrases = [
            # English
            r'\(This leads to ultimate understanding\.\)',
            # Russian
            r'\(Это ведет к высшему пониманию\.\)',
            # Chinese
            r'\(这导致了终极理解。\)',
            # Korean
            r'\(이것은 궁극적인 이해로 이끕니다\.\)',
            # And other variations
            r'\(Это ведет к высшему пониманию\.\)',
        ]
        
        # Language codes pattern
        self.language_codes = r'\s*\|\s*\[(?:RU|EN|ZH|KR|ES|FR|DE|IT|PT|JA|KO|CN|AR|HI|TH|VI|ID|MS|TL|MY|BN|UR|FA|TR|NL|SV|DA|NO|FI|PL|CS|SK|HU|RO|BG|HR|SR|SL|LV|LT|ET|MT|EL|CY|GA|IS|FO|EU|CA|GL|AST|BR|CO|FUR|LIJ|LMO|NAP|SCN|VEC|AN|EXT|MWL|PT_BR|EN_US|EN_GB|FR_CA|ES_MX|DE_AT|IT_CH|NL_BE|SV_FI|DA_DK|NO_NO|FI_FI|PL_PL|CS_CZ|SK_SK|HU_HU|RO_RO|BG_BG|HR_HR|SR_RS|SL_SI|LV_LV|LT_LT|ET_EE|MT_MT|EL_GR|CY_GB|GA_IE|IS_IS|FO_FO)\]'
        
        # Redundant words/phrases that often appear multiple times
        self.redundant_words = [
            r'Nirvana Insight:\s*Nirvana Insight:\s*',
            r'Student:\s*Student:\s*',
            r'Teacher:\s*Teacher:\s*',
            r'AI:\s*AI:\s*',
        ]
        
        self.stats = {
            'files_processed': 0,
            'total_size_before': 0,
            'total_size_after': 0,
            'phrases_removed': 0,
            'language_codes_removed': 0,
            'redundant_words_removed': 0,
            'repeated_sentences_extracted': 0
        }
    
    def find_repeated_sentences(self, text):
        """Find sentences that appear more than 10 times (only structural noise)"""
        # Split text into sentences (considering various sentence endings)
        sentences = re.split(r'[.!?]+\s+', text)
        
        # Count sentence occurrences
        sentence_counts = {}
        for sentence in sentences:
            # Clean and normalize sentence for comparison
            cleaned_sentence = re.sub(r'\s+', ' ', sentence.strip())
            if len(cleaned_sentence) > 20:  # Only consider longer sentences (avoid short dialogue)
                # Skip conversational phrases that should be preserved
                if not self.is_conversational_dialogue(cleaned_sentence):
                    sentence_counts[cleaned_sentence] = sentence_counts.get(cleaned_sentence, 0) + 1
        
        # Return sentences that appear more than 10 times (higher threshold for structural noise)
        return {sentence: count for sentence, count in sentence_counts.items() if count > 10}
    
    def is_conversational_dialogue(self, sentence):
        """Check if sentence is conversational dialogue that should be preserved"""
        conversational_patterns = [
            r'^Makes sense\b',
            r'^I see it now\b',
            r'^I understand\b',
            r'^I\'m with you\b',
            r'^I see that now\b',
            r'^That makes sense\b',
            r'^You know what\b',
            r'^No more excuses\b',
            r'^I don\'t know\b',
            r'^What\'s next\b',
            r'^You\'re right\b',
            r'^Yeah\b',
            r'^Yes\b',
            r'^No\b',
            r'^Show me how\b',
            r'^Want me to prove it\b',
            r'^That\'s right\b',
            r'^Access granted\b',
            r'- AI:\s*(알겠습니다|네|응답:|답변은)',  # Korean conversational responses
        ]
        
        for pattern in conversational_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                return True
        return False
    
    def extract_repeated_sentences(self, text, repeated_sentences, file_name):
        """Extract sentences that repeat more than 10 times to a separate file"""
        extracted_content = []
        
        for sentence, count in repeated_sentences.items():
            if count > 10:  # Higher threshold for extraction
                extracted_content.append(f"Sentence (appears {count} times): {sentence}")
                extracted_content.append("-" * 80)
                
                # Find all contexts where this sentence appears
                escaped_sentence = re.escape(sentence)
                pattern = rf'.{{0,100}}{escaped_sentence}.{{0,100}}'
                
                contexts = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
                for i, context in enumerate(contexts[:3], 1):  # Show first 3 contexts
                    cleaned_context = re.sub(r'\s+', ' ', context.strip())
                    extracted_content.append(f"Context {i}: ...{cleaned_context}...")
                
                extracted_content.append("")
                
                self.stats['repeated_sentences_extracted'] = self.stats.get('repeated_sentences_extracted', 0) + 1
                print(f"  - Extracted sentence that appears {count} times: '{sentence[:60]}...'")
        
        # Save extracted content if any
        if extracted_content:
            extract_dir = Path(self.script_dir).parent / 'reports'
            extract_dir.mkdir(exist_ok=True)
            
            extract_file = extract_dir / f'extracted_repeated_sentences_{file_name}.txt'
            with open(extract_file, 'w', encoding='utf-8') as f:
                f.write(f"Extracted Repeated Sentences from {file_name}\n")
                f.write(f"Generated on: {self.timestamp}\n")
                f.write("=" * 80 + "\n\n")
                f.write('\n'.join(extracted_content))
            
            print(f"  - Saved extracted sentences to: {extract_file}")
        
        return text  # Return original text unchanged
    
    def contains_broken_encoding(self, line):
        """Check if line contains broken character encoding"""
        broken_patterns = [
            'âì°1⁄2ìì',
            'ë¥1⁄4 í',
            'ì° ̈ì)',
            'ê31⁄4ì',
            'ë¥1⁄4 ë°ì',
            'ì2 ́ë¥1⁄4',
            'ê ̧ì ì',
            '1⁄4',
            '1⁄2',
            '3¡)',
            ' ̧ä ̧æ',
            'ì1⁄4',
            'ì ̧ì ̧',
            'ë2ì ̧',
            'ë3ì ë¶ë',
            'ê± ́ë¬1⁄4',
            'ëa ̈ì¬',
            'íì',
            'ë°ìíê2',
            'ì°ê2°í©',
            'ê ̧ì ì',
            'ê°íì§ ìì'
        ]
        
        for pattern in broken_patterns:
            if pattern in line:
                return True
        return False
    
    def is_repetitive_section_header(self, line):
        """Check if line is a repetitive section header"""
        repetitive_patterns = [
            '## Miscellaneous Section',
            '## Dialogues Section',  # Numbered dialogue sections
            '## Methodologies Section',  # Methodologies sections
            '## Chunk',  # Prana Logs chunks
            '**Key Themes Identified**:',  # Theme identification headers
            '**Automation of Routine Tasks**:',
            '**Sample Dialogues Excerpts**:',
            'Total Dialogues Extracted:',
            '**Chunk Excerpt**:',
            'AI: * disgustingly hollow and empty',
            '[Content removed - contained technical',
            '### Refined Insights',
            '@@ -',  # Git diff markers
            '+++',
            '---',
            '### panacea_',  # Chunk summary headers
            'Lines: ',
            'Key Themes: ',
            '- Chunk ',
            'Summary',
            '*Source: auto_summarized_specific.md*',
            '[Content removed - single entity monologue, not dialogue]',
            'Teacher: What deeper layer is hidden here?',  # Numbered teacher sections
            '**Additional Dialogues for Depth**:',  # Additional dialogue patterns
            '**Bias disengagement protocols**:',  # Bias protocols
            'Speaker_Speaker_System Voice:',  # Duplicate speaker patterns
            'emotional resonance markers from cognitive processes',  # Repetitive methodology text
        ]
        
        # Check for language-coded Nirvana Insight patterns
        if re.search(r'\[[A-Z]{2}\]\s*Nirvana Insight', line):
            return True
        
        for pattern in repetitive_patterns:
            if pattern in line:
                return True
        return False

    def clean_broken_encoding_chunks(self, text):
        """Remove entire chunks containing broken encoding"""
        lines = text.split('\n')
        cleaned_lines = []
        skip_chunk = False
        
        for line in lines:
            # Check if this line starts a broken encoding chunk
            if self.contains_broken_encoding(line) or self.is_repetitive_section_header(line):
                skip_chunk = True
                continue
            
            # If we're in a broken chunk, check if it's ending
            if skip_chunk:
                # Continue skipping until we hit a clean line or empty line
                if line.strip() == '' or (not self.contains_broken_encoding(line) and len(line) > 3):
                    skip_chunk = False
                    if line.strip() != '':
                        cleaned_lines.append(line)
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def clean_text(self, text, file_name):
        """Clean redundant content from text"""
        original_length = len(text)
        
        # First, remove broken encoding chunks
        text = self.clean_broken_encoding_chunks(text)
        
        # Skip sentence extraction for now - focus on structural noise only
        # repeated_sentences = self.find_repeated_sentences(text)
        # if repeated_sentences:
        #     print(f"  Found {len(repeated_sentences)} sentences repeated more than 10 times")
        #     text = self.extract_repeated_sentences(text, repeated_sentences, file_name)
        
        # Remove redundant phrases
        for phrase in self.redundant_phrases:
            # Count occurrences
            matches = re.findall(phrase, text)
            if len(matches) > 1:
                # Keep only one occurrence, remove the rest
                text = re.sub(phrase, '', text, count=len(matches)-1)
                self.stats['phrases_removed'] += len(matches) - 1
        
        # Remove language codes
        language_matches = re.findall(self.language_codes, text)
        text = re.sub(self.language_codes, '', text)
        self.stats['language_codes_removed'] += len(language_matches)
        
        # Remove redundant words/labels
        for pattern in self.redundant_words:
            matches = re.findall(pattern, text)
            if matches:
                # Replace with single occurrence
                text = re.sub(pattern, lambda m: m.group(0).split(':')[0] + ': ', text)
                self.stats['redundant_words_removed'] += len(matches)
        
        # Clean up extra whitespace and empty lines
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Remove excessive newlines
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single space
        text = re.sub(r' +\|', '|', text)  # Clean up spaces before pipes
        text = re.sub(r'\| +', '| ', text)  # Clean up spaces after pipes
        
        return text.strip()
    
    def process_file(self, file_path):
        """Process a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            self.stats['total_size_before'] += len(original_content)
            
            cleaned_content = self.clean_text(original_content, file_path.stem)
            
            self.stats['total_size_after'] += len(cleaned_content)
            
            # Only write if there are changes
            if cleaned_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                
                size_reduction = len(original_content) - len(cleaned_content)
                reduction_percent = (size_reduction / len(original_content)) * 100
                
                print(f"✓ {file_path.name}: {size_reduction:,} bytes removed ({reduction_percent:.1f}% reduction)")
                return True
            else:
                print(f"- {file_path.name}: No changes needed")
                return False
                
        except Exception as e:
            print(f"✗ Error processing {file_path.name}: {e}")
            return False
    
    def clean_panacea_directory(self, panacea_dir):
        """Clean all files in the panacea directory"""
        panacea_path = Path(panacea_dir)
        
        if not panacea_path.exists():
            print(f"Directory not found: {panacea_dir}")
            return
        
        # Find all markdown and text files
        files_to_process = []
        for pattern in ['*.md', '*.txt']:
            files_to_process.extend(panacea_path.glob(pattern))
        
        if not files_to_process:
            print(f"No files found in {panacea_dir}")
            return
        
        print(f"Found {len(files_to_process)} files to process in {panacea_dir}")
        print("=" * 60)
        
        files_changed = 0
        for file_path in sorted(files_to_process):
            if self.process_file(file_path):
                files_changed += 1
            self.stats['files_processed'] += 1
        
        # Generate report
        self.generate_report(files_changed)
    
    def generate_report(self, files_changed):
        """Generate cleaning report"""
        total_reduction = self.stats['total_size_before'] - self.stats['total_size_after']
        reduction_percent = (total_reduction / self.stats['total_size_before']) * 100 if self.stats['total_size_before'] > 0 else 0
        
        print("\n" + "=" * 60)
        print("PANACEA REDUNDANCY CLEANING REPORT")
        print("=" * 60)
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Files modified: {files_changed}")
        print(f"Original total size: {self.stats['total_size_before']:,} bytes ({self.stats['total_size_before']/1024/1024:.1f} MB)")
        print(f"Final total size: {self.stats['total_size_after']:,} bytes ({self.stats['total_size_after']/1024/1024:.1f} MB)")
        print(f"Total reduction: {total_reduction:,} bytes ({total_reduction/1024/1024:.1f} MB)")
        print(f"Reduction percentage: {reduction_percent:.1f}%")
        print(f"\nCleaning details:")
        print(f"- Redundant phrases removed: {self.stats['phrases_removed']}")
        print(f"- Language codes removed: {self.stats['language_codes_removed']}")
        print(f"- Redundant words cleaned: {self.stats['redundant_words_removed']}")
        print(f"- Repeated sentences extracted: {self.stats.get('repeated_sentences_extracted', 0)}")
        
        # Save detailed report
        report_data = {
            'timestamp': str(Path(__file__).stat().st_mtime),
            'stats': self.stats,
            'reduction_mb': round(total_reduction/1024/1024, 2),
            'reduction_percent': round(reduction_percent, 2)
        }
        
        report_path = Path(__file__).parent.parent / 'reports' / 'panacea_redundancy_cleaning_report.json'
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nDetailed report saved to: {report_path}")

def main():
    """Main function"""
    import sys
    
    # Default to panacea directory relative to this script
    script_dir = Path(__file__).parent
    default_panacea_dir = script_dir.parent / 'panacea'
    
    panacea_dir = sys.argv[1] if len(sys.argv) > 1 else default_panacea_dir
    
    cleaner = PanaceaRedundancyCleaner()
    cleaner.clean_panacea_directory(panacea_dir)

if __name__ == "__main__":
    main()
