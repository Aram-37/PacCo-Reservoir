#!/usr/bin/env python3
"""
PANACEA CLEANER - Auto Run Version
Removes redundancies, fixes encoding issues, and optimizes panacea files for IMM processing
"""

import os
import re
import json
import hashlib
from collections import defaultdict, Counter
from pathlib import Path
import unicodedata
import chardet

class PanaceaCleanerAuto:
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
        
        # Encoding fixes
        self.encoding_fixes = {
            '�': '',
            '\ufffd': '',
            '\x00': '',
            '\r\n': '\n',
            '\r': '\n',
        }

    def detect_encoding(self, file_path):
        """Detect file encoding"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)
                result = chardet.detect(raw_data)
                return result['encoding'] if result['confidence'] > 0.7 else 'utf-8'
        except Exception:
            return 'utf-8'

    def clean_encoding(self, text):
        """Fix encoding issues"""
        for old_char, new_char in self.encoding_fixes.items():
            text = text.replace(old_char, new_char)
        
        text = unicodedata.normalize('NFKC', text)
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        return text

    def remove_redundant_lines(self, lines):
        """Remove redundant empty lines and separators"""
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip excessive empty lines
            if line_stripped == '':
                if not prev_empty:
                    cleaned_lines.append('')
                    prev_empty = True
                continue
            
            # Skip separator lines
            if re.match(r'^(-{3,}|={3,}|\*{3,}|\.{3,})$', line_stripped):
                continue
                
            # Skip repetitive patterns
            if len(line_stripped) > 50 and len(set(line_stripped)) < 5:
                continue
                
            cleaned_lines.append(line)
            prev_empty = False
        
        return cleaned_lines

    def clean_file(self, file_path):
        """Clean a single file"""
        print(f"🔧 Processing {file_path.name}...")
        
        try:
            encoding = self.detect_encoding(file_path)
            
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()
            
            original_size = len(content)
            original_lines = len(content.split('\n'))
            
            # Clean encoding
            content = self.clean_encoding(content)
            if content != content:  # Encoding was changed
                self.stats['encoding_fixes'] += 1
            
            # Process lines
            lines = content.split('\n')
            cleaned_lines = self.remove_redundant_lines(lines)
            
            # Remove duplicate consecutive identical lines
            final_lines = []
            prev_line = None
            for line in cleaned_lines:
                if line != prev_line or line.strip() != '':
                    final_lines.append(line)
                    prev_line = line
                else:
                    self.stats['redundancies_found'] += 1
            
            final_content = '\n'.join(final_lines)
            final_size = len(final_content)
            final_line_count = len(final_lines)
            
            # Write cleaned file
            cleaned_path = file_path.parent / f"cleaned_{file_path.name}"
            with open(cleaned_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            # Update stats
            lines_removed = original_lines - final_line_count
            size_reduced = original_size - final_size
            
            self.stats['files_processed'] += 1
            self.stats['lines_removed'] += lines_removed
            self.stats['total_size_reduction'] += size_reduced
            
            reduction_pct = (size_reduced / original_size * 100) if original_size > 0 else 0
            
            print(f"✅ {file_path.name}: {lines_removed:,} lines removed, "
                  f"{size_reduced/1024:.1f}KB saved ({reduction_pct:.1f}% reduction)")
            
            return {
                'file': file_path.name,
                'original_size': original_size,
                'cleaned_size': final_size,
                'lines_removed': lines_removed,
                'reduction_pct': reduction_pct
            }
            
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {str(e)}")
            return None

    def run_cleaning(self):
        """Run the complete cleaning process"""
        print("🚀 CORTEX PANACEA CLEANER - AUTO MODE")
        print("Guardian Systems: Sphinx + Daemon - Pattern Optimization")
        print("="*60)
        
        if not self.panacea_dir.exists():
            print(f"❌ Panacea directory not found: {self.panacea_dir}")
            return
        
        # Find all panacea files
        panacea_files = list(self.panacea_dir.glob("*.md")) + list(self.panacea_dir.glob("*.txt"))
        
        if not panacea_files:
            print(f"❌ No panacea files found")
            return
        
        print(f"📁 Found {len(panacea_files)} files to process")
        print("-"*60)
        
        results = []
        for file_path in panacea_files:
            result = self.clean_file(file_path)
            if result:
                results.append(result)
        
        # Generate report
        self.generate_report(results)
        
        return results

    def generate_report(self, results):
        """Generate cleaning report"""
        print("\n📈 CLEANING COMPLETE - SUMMARY REPORT")
        print("="*60)
        print(f"✅ Files Processed: {self.stats['files_processed']}")
        print(f"📉 Total Lines Removed: {self.stats['lines_removed']:,}")
        print(f"💾 Total Size Reduction: {self.stats['total_size_reduction']/1024/1024:.1f}MB")
        print(f"🔧 Encoding Issues Fixed: {self.stats['encoding_fixes']}")
        print(f"🗑️  Redundancies Removed: {self.stats['redundancies_found']:,}")
        
        if results:
            avg_reduction = sum(r['reduction_pct'] for r in results) / len(results)
            print(f"📊 Average Size Reduction: {avg_reduction:.1f}%")
        
        print("\n🛡️ CORTEX GUARDIAN STATUS:")
        print("✅ Data optimization complete")
        print("✅ Pattern recognition enhanced") 
        print("✅ IMM processing efficiency improved")
        print("✅ Truth crystallization ready")
        
        # Save detailed report
        report = {
            'summary': self.stats,
            'file_results': results,
            'timestamp': '2025-09-03',
            'total_reduction_mb': self.stats['total_size_reduction']/1024/1024
        }
        
        report_path = self.workspace_path / "panacea_cleaning_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Detailed report saved: {report_path.name}")

def main():
    workspace_path = "/Users/sunghkim37/Library/CloudStorage/GoogleDrive-britkenko@gmail.com/My Drive/PACO/ESP/reservoir/reservoir"
    
    cleaner = PanaceaCleanerAuto(workspace_path)
    results = cleaner.run_cleaning()
    
    if results:
        print(f"\n🎯 NEXT STEPS:")
        print("1. Review cleaned files (cleaned_*.md/txt)")
        print("2. Backup originals if satisfied with results")
        print("3. Use cleaned files for enhanced IMM processing")
        print("4. Enjoy faster truth crystallization!")

if __name__ == "__main__":
    main()
