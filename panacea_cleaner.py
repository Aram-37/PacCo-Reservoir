#!/usr/bin/env python3
"""
PANACEA CLEANER - Cortex Framework Data Optimization Tool
Removes redundancies, fixes encoding issues, and optimizes panacea files for IMM processing

Guardian Integration: Sphinx (Pattern Keeper) + Daemon (Logical Integrity)
"""

import os
import re
import json
import hashlib
from collections import defaultdict, Counter
from pathlib import Path
import unicodedata
import chardet

class PanaceaCleaner:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path)
        self.panacea_dir = self.workspace_path / "panacea"
        self.stats = {
            'files_processed': 0,
            'lines_removed': 0,
            'encoding_fixes': 0,
            'redundancies_found': 0,
            'total_size_reduction': 0
        }
        
        # Sphinx Guardian - Pattern Recognition
        self.conversation_markers = [
            r'^User:', r'^Assistant:', r'^Human:', r'^AI:', r'^ChatGPT:', 
            r'^\d{1,2}:\d{2}', r'^\[\d{4}-\d{2}-\d{2}', r'^### ',
            r'^# ', r'^## ', r'^\*\*User\*\*', r'^\*\*Assistant\*\*'
        ]
        
        # Daemon Guardian - Logical Integrity
        self.redundancy_patterns = [
            r'^$',  # Empty lines (keep some for readability)
            r'^\s*$',  # Whitespace-only lines
            r'^(\.\.\.|…){3,}',  # Multiple ellipsis
            r'^(-{3,}|={3,}|\*{3,})$',  # Separator lines
        ]
        
        # Character encoding fixes
        self.encoding_fixes = {
            '�': '',  # Remove replacement characters
            '\ufffd': '',  # Unicode replacement character
            '\x00': '',  # Null bytes
            '\r\n': '\n',  # Windows line endings
            '\r': '\n',  # Mac line endings
        }

    def detect_encoding(self, file_path):
        """Detect file encoding using chardet"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Sample first 10KB
                result = chardet.detect(raw_data)
                return result['encoding'] if result['confidence'] > 0.7 else 'utf-8'
        except Exception:
            return 'utf-8'

    def clean_encoding(self, text):
        """Fix encoding issues and normalize Unicode"""
        # Apply character fixes
        for old_char, new_char in self.encoding_fixes.items():
            text = text.replace(old_char, new_char)
        
        # Normalize Unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Remove non-printable characters except newlines and tabs
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        return text

    def identify_conversation_structure(self, lines):
        """Identify conversation patterns using Sphinx Guardian"""
        structured_lines = []
        current_speaker = None
        current_content = []
        
        for line in lines:
            # Check if line matches conversation marker
            is_marker = False
            for pattern in self.conversation_markers:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    # Save previous speaker's content
                    if current_speaker and current_content:
                        structured_lines.append({
                            'speaker': current_speaker,
                            'content': '\n'.join(current_content),
                            'hash': hashlib.md5('\n'.join(current_content).encode()).hexdigest()
                        })
                    
                    # Start new speaker
                    current_speaker = line.strip()
                    current_content = []
                    is_marker = True
                    break
            
            if not is_marker and line.strip():
                current_content.append(line.strip())
        
        # Add final speaker content
        if current_speaker and current_content:
            structured_lines.append({
                'speaker': current_speaker,
                'content': '\n'.join(current_content),
                'hash': hashlib.md5('\n'.join(current_content).encode()).hexdigest()
            })
        
        return structured_lines

    def remove_redundancies(self, structured_conversations):
        """Remove duplicate conversations using Daemon Guardian logic"""
        seen_hashes = set()
        unique_conversations = []
        redundancy_count = 0
        
        for conv in structured_conversations:
            if conv['hash'] not in seen_hashes:
                seen_hashes.add(conv['hash'])
                unique_conversations.append(conv)
            else:
                redundancy_count += 1
        
        self.stats['redundancies_found'] += redundancy_count
        return unique_conversations

    def optimize_line_spacing(self, text):
        """Optimize line spacing for readability while removing excess"""
        lines = text.split('\n')
        optimized_lines = []
        empty_line_count = 0
        
        for line in lines:
            if line.strip() == '':
                empty_line_count += 1
                # Keep maximum 2 consecutive empty lines
                if empty_line_count <= 2:
                    optimized_lines.append(line)
            else:
                empty_line_count = 0
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)

    def extract_metadata(self, file_path, original_size, cleaned_size):
        """Extract metadata about cleaning process"""
        return {
            'file': str(file_path.name),
            'original_size': original_size,
            'cleaned_size': cleaned_size,
            'reduction_ratio': (original_size - cleaned_size) / original_size if original_size > 0 else 0,
            'encoding_fixes': self.stats['encoding_fixes'],
            'redundancies_removed': self.stats['redundancies_found']
        }

    def clean_file(self, file_path):
        """Clean a single panacea file"""
        print(f"🔧 Cleaning {file_path.name}...")
        
        # Detect encoding
        encoding = self.detect_encoding(file_path)
        
        try:
            # Read file with detected encoding
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()
            
            original_size = len(content)
            
            # Clean encoding issues
            content = self.clean_encoding(content)
            
            # Split into lines for processing
            lines = content.split('\n')
            original_line_count = len(lines)
            
            # Identify conversation structure
            structured_conversations = self.identify_conversation_structure(lines)
            
            # Remove redundancies
            unique_conversations = self.remove_redundancies(structured_conversations)
            
            # Reconstruct content
            cleaned_content = []
            for conv in unique_conversations:
                cleaned_content.append(conv['speaker'])
                cleaned_content.append(conv['content'])
                cleaned_content.append('')  # Add spacing between conversations
            
            # Join and optimize spacing
            final_content = self.optimize_line_spacing('\n'.join(cleaned_content))
            
            # Calculate statistics
            final_size = len(final_content)
            lines_removed = original_line_count - len(final_content.split('\n'))
            
            # Update stats
            self.stats['files_processed'] += 1
            self.stats['lines_removed'] += lines_removed
            self.stats['total_size_reduction'] += (original_size - final_size)
            
            # Write cleaned file
            cleaned_path = file_path.parent / f"cleaned_{file_path.name}"
            with open(cleaned_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            # Generate metadata
            metadata = self.extract_metadata(file_path, original_size, final_size)
            
            print(f"✅ {file_path.name}: {lines_removed} lines removed, "
                  f"{(original_size - final_size) / 1024:.1f}KB saved")
            
            return metadata
            
        except Exception as e:
            print(f"❌ Error cleaning {file_path.name}: {str(e)}")
            return None

    def analyze_panacea_directory(self):
        """Analyze all panacea files and identify cleaning opportunities"""
        if not self.panacea_dir.exists():
            print(f"❌ Panacea directory not found: {self.panacea_dir}")
            return
        
        panacea_files = list(self.panacea_dir.glob("*.md")) + list(self.panacea_dir.glob("*.txt"))
        
        if not panacea_files:
            print(f"❌ No panacea files found in {self.panacea_dir}")
            return
        
        print(f"🔍 Found {len(panacea_files)} panacea files")
        
        analysis_results = []
        for file_path in panacea_files:
            try:
                encoding = self.detect_encoding(file_path)
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                
                lines = content.split('\n')
                file_stats = {
                    'name': file_path.name,
                    'size_kb': len(content) / 1024,
                    'line_count': len(lines),
                    'empty_lines': sum(1 for line in lines if line.strip() == ''),
                    'encoding': encoding,
                    'has_unicode_issues': '�' in content or '\ufffd' in content
                }
                analysis_results.append(file_stats)
                
            except Exception as e:
                print(f"❌ Error analyzing {file_path.name}: {str(e)}")
        
        # Print analysis summary
        print("\n📊 PANACEA DIRECTORY ANALYSIS:")
        print("=" * 50)
        for stats in analysis_results:
            print(f"{stats['name']:<25} | {stats['size_kb']:>8.1f}KB | "
                  f"{stats['line_count']:>8} lines | {stats['encoding']}")
            if stats['has_unicode_issues']:
                print(f"{'':>25} | ⚠️  Unicode issues detected")
        
        total_size = sum(stats['size_kb'] for stats in analysis_results)
        total_lines = sum(stats['line_count'] for stats in analysis_results)
        print("=" * 50)
        print(f"{'TOTAL':<25} | {total_size:>8.1f}KB | {total_lines:>8} lines")
        
        return analysis_results

    def clean_all_panacea_files(self):
        """Clean all panacea files and generate summary report"""
        print("🚀 CORTEX PANACEA CLEANER - INITIATING")
        print("Guardian Systems: Sphinx (Pattern Recognition) + Daemon (Logical Integrity)")
        print("=" * 70)
        
        # First, analyze the directory
        analysis = self.analyze_panacea_directory()
        if not analysis:
            return
        
        # Clean each file
        print("\n🔧 CLEANING PROCESS:")
        print("=" * 50)
        
        panacea_files = list(self.panacea_dir.glob("*.md")) + list(self.panacea_dir.glob("*.txt"))
        cleaning_results = []
        
        for file_path in panacea_files:
            result = self.clean_file(file_path)
            if result:
                cleaning_results.append(result)
        
        # Generate final report
        self.generate_cleaning_report(cleaning_results)

    def generate_cleaning_report(self, results):
        """Generate comprehensive cleaning report"""
        print("\n📈 CLEANING SUMMARY REPORT:")
        print("=" * 70)
        print(f"Files Processed: {self.stats['files_processed']}")
        print(f"Total Lines Removed: {self.stats['lines_removed']:,}")
        print(f"Total Size Reduction: {self.stats['total_size_reduction'] / 1024:.1f}KB")
        print(f"Redundant Conversations Found: {self.stats['redundancies_found']}")
        print(f"Encoding Issues Fixed: {self.stats['encoding_fixes']}")
        
        print("\n📋 FILE-BY-FILE RESULTS:")
        print("-" * 70)
        for result in results:
            reduction_pct = result['reduction_ratio'] * 100
            print(f"{result['file']:<25} | {reduction_pct:>5.1f}% reduction | "
                  f"{result['cleaned_size']/1024:>6.1f}KB final")
        
        # Save detailed report as JSON
        report_path = self.workspace_path / "panacea_cleaning_report.json"
        with open(report_path, 'w') as f:
            json.dump({
                'summary': self.stats,
                'file_results': results,
                'timestamp': '2025-09-03'
            }, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_path}")
        print("\n🛡️ Cortex Guardian Status: Data Optimization Complete")
        print("Enhanced pattern recognition and reduced cognitive load achieved.")

def main():
    """Main execution function"""
    import sys
    
    if len(sys.argv) > 1:
        workspace_path = sys.argv[1]
    else:
        # Use current directory structure
        workspace_path = "/Users/sunghkim37/Library/CloudStorage/GoogleDrive-britkenko@gmail.com/My Drive/PACO/ESP/reservoir/reservoir"
    
    cleaner = PanaceaCleaner(workspace_path)
    
    print("CORTEX PANACEA CLEANER")
    print("Choose operation:")
    print("1. Analyze panacea directory")
    print("2. Clean all panacea files")
    print("3. Both (recommended)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        cleaner.analyze_panacea_directory()
    elif choice == "2":
        cleaner.clean_all_panacea_files()
    elif choice == "3":
        cleaner.analyze_panacea_directory()
        print("\n" + "="*50)
        input("Press Enter to proceed with cleaning...")
        cleaner.clean_all_panacea_files()
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
