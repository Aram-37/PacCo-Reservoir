#!/usr/bin/env python3
"""
Dark Panacea ChatGPT Cleaner
Specialized script to clean the massive dark_panacea_chatgpt.txt file
with extreme repetition patterns like "ChatGPT Yes..." repeated 1000+ times.
"""

import re
import json
from pathlib import Path

class DarkPanaceaCleaner:
    def __init__(self):
        self.stats = {
            'original_size': 0,
            'final_size': 0,
            'chatgpt_responses_removed': 0,
            'repetitive_patterns_removed': 0
        }
        
        # Common ChatGPT response patterns that repeat excessively
        self.chatgpt_patterns = [
            r'ChatGPT Yes\.{3}',
            r'ChatGPT You\'re right\.{3}',
            r'ChatGPT Understood\.{3}',
            r'ChatGPT Yeah\.{3}',
            r'ChatGPT I understand\.{3}',
            r'ChatGPT Alright\.{3}',
            r'ChatGPT I know\.{3}',
            r'ChatGPT I hear you\.{3}',
            r'You\'re right\.{3}',
            r'That\'s on me\.{3}',
            r'That matters\.{3}',
            r'it can be anything\.{3}',
        ]
    
    def count_pattern_occurrences(self, text):
        """Count how many times each pattern appears"""
        pattern_counts = {}
        
        for pattern in self.chatgpt_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                pattern_counts[pattern] = len(matches)
        
        return pattern_counts
    
    def clean_repetitive_chatgpt_responses(self, text):
        """Remove excessive ChatGPT response repetitions, keep only 2-3 instances"""
        
        print("Analyzing repetitive patterns...")
        pattern_counts = self.count_pattern_occurrences(text)
        
        for pattern, count in pattern_counts.items():
            if count > 3:
                print(f"  - Pattern '{pattern}' appears {count} times, reducing to 2...")
                
                # Keep only 2 instances of each pattern
                text = re.sub(pattern, '', text, count=count-2, flags=re.IGNORECASE)
                self.stats['chatgpt_responses_removed'] += count - 2
        
        return text
    
    def remove_excessive_whitespace(self, text):
        """Clean up excessive whitespace and empty lines"""
        # Remove multiple consecutive newlines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove multiple spaces
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove trailing whitespace from lines
        text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def process_dark_panacea_file(self, file_path):
        """Process the dark_panacea_chatgpt.txt file"""
        
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return False
        
        print(f"Processing: {file_path.name}")
        print(f"Original size: {file_path.stat().st_size / 1024 / 1024:.1f} MB")
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        self.stats['original_size'] = len(original_content)
        
        # Clean repetitive patterns
        cleaned_content = self.clean_repetitive_chatgpt_responses(original_content)
        
        # Clean whitespace
        cleaned_content = self.remove_excessive_whitespace(cleaned_content)
        
        self.stats['final_size'] = len(cleaned_content)
        
        # Calculate reduction
        size_reduction = self.stats['original_size'] - self.stats['final_size']
        reduction_percent = (size_reduction / self.stats['original_size']) * 100
        
        print(f"\nCleaning Results:")
        print(f"  Original size: {self.stats['original_size']:,} bytes ({self.stats['original_size']/1024/1024:.1f} MB)")
        print(f"  Final size: {self.stats['final_size']:,} bytes ({self.stats['final_size']/1024/1024:.1f} MB)")
        print(f"  Reduction: {size_reduction:,} bytes ({size_reduction/1024/1024:.1f} MB)")
        print(f"  Reduction: {reduction_percent:.1f}%")
        print(f"  ChatGPT responses removed: {self.stats['chatgpt_responses_removed']}")
        
        if size_reduction > 0:
            # Save the cleaned version
            backup_path = file_path.with_suffix('.txt.backup')
            
            # Create backup
            print(f"\nCreating backup: {backup_path.name}")
            file_path.rename(backup_path)
            
            # Write cleaned version
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            print(f"✓ Cleaned file saved: {file_path.name}")
            
            # Save report
            self.save_report()
            
            return True
        else:
            print("No changes needed.")
            return False
    
    def save_report(self):
        """Save cleaning report"""
        report_data = {
            'file_processed': 'dark_panacea_chatgpt.txt',
            'original_size_mb': round(self.stats['original_size'] / 1024 / 1024, 2),
            'final_size_mb': round(self.stats['final_size'] / 1024 / 1024, 2),
            'reduction_mb': round((self.stats['original_size'] - self.stats['final_size']) / 1024 / 1024, 2),
            'reduction_percent': round(((self.stats['original_size'] - self.stats['final_size']) / self.stats['original_size']) * 100, 2),
            'chatgpt_responses_removed': self.stats['chatgpt_responses_removed']
        }
        
        report_path = Path(__file__).parent.parent / 'reports' / 'dark_panacea_cleaning_report.json'
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"Report saved: {report_path}")

def main():
    """Main function"""
    script_dir = Path(__file__).parent
    dark_panacea_file = script_dir.parent / 'panacea' / 'dark_panacea_chatgpt.txt'
    
    cleaner = DarkPanaceaCleaner()
    cleaner.process_dark_panacea_file(dark_panacea_file)

if __name__ == "__main__":
    main()
