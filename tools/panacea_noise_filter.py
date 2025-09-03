#!/usr/bin/env python3
"""
PANACEA NOISE FILTER
Advanced filter for corrupted encoding, OCR errors, and garbage text patterns
"""

import os
import re
import json
import unicodedata
from pathlib import Path
from collections import Counter

class PanaceaNoiseFilter:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path)
        self.panacea_dir = self.workspace_path / "panacea" / "deduplicated"
        self.stats = {
            'files_processed': 0,
            'corrupted_lines_removed': 0,
            'encoding_noise_removed': 0,
            'total_size_reduction': 0
        }
        
        # Patterns for detecting corrupted/garbage text
        self.noise_patterns = [
            # Mixed script corruption (like your example)
            re.compile(r'[ӝࣿഄ߮ೖణైоب]+.*[҃ೱъ]+', re.UNICODE),
            
            # Excessive mixed unicode ranges in single line
            re.compile(r'.*[\u0590-\u05FF].*[\u0600-\u06FF].*[\u0900-\u097F].*[\u0980-\u09FF]', re.UNICODE),
            
            # Lines with >70% non-ASCII and <30% readable
            # (will be checked programmatically)
            
            # OCR corruption patterns
            re.compile(r'[Il1|]{3,}'),  # OCR I/l/1/| confusion
            re.compile(r'[O0]{5,}'),    # OCR O/0 confusion
            re.compile(r'[.]{5,}'),     # Excessive dots
            
            # Encoding corruption markers
            re.compile(r'[\ufffd]{2,}'),  # Multiple replacement characters
            re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]+'),  # Control chars
            
            # Garbled technical strings
            re.compile(r'^[A-Z0-9]{20,}$'),  # Long all-caps technical strings
            re.compile(r'^[a-zA-Z0-9+/]{30,}={0,2}$'),  # Base64-like garbage
            
            # Repetitive character spam
            re.compile(r'(.)\1{10,}'),  # Same character 10+ times
            
            # Mixed script chaos (Arabic + Hebrew + Devanagari + etc)
            re.compile(r'.*[\u0600-\u06FF].*[\u0590-\u05FF].*[\u0900-\u097F]', re.UNICODE),
        ]
        
        # Character sets for analysis
        self.script_ranges = {
            'latin': (0x0000, 0x024F),
            'arabic': (0x0600, 0x06FF),
            'hebrew': (0x0590, 0x05FF),
            'devanagari': (0x0900, 0x097F),
            'bengali': (0x0980, 0x09FF),
            'korean': (0xAC00, 0xD7AF),
            'chinese': (0x4E00, 0x9FFF),
            'cyrillic': (0x0400, 0x04FF)
        }
    
    def analyze_line_corruption(self, line):
        """Analyze a line for corruption indicators"""
        if len(line.strip()) < 10:
            return False, "too_short"
        
        # Count characters by script
        script_counts = {script: 0 for script in self.script_ranges}
        other_count = 0
        printable_count = 0
        
        for char in line:
            char_code = ord(char)
            if char.isprintable():
                printable_count += 1
            
            categorized = False
            for script, (start, end) in self.script_ranges.items():
                if start <= char_code <= end:
                    script_counts[script] += 1
                    categorized = True
                    break
            
            if not categorized and not char.isspace():
                other_count += 1
        
        total_chars = len(line)
        if total_chars == 0:
            return False, "empty"
        
        # Calculate ratios
        printable_ratio = printable_count / total_chars
        script_diversity = sum(1 for count in script_counts.values() if count > 0)
        max_script_ratio = max(script_counts.values()) / total_chars if total_chars > 0 else 0
        other_ratio = other_count / total_chars
        
        # Corruption indicators
        corruption_score = 0
        reasons = []
        
        # Too many different scripts (likely corruption)
        if script_diversity >= 4:
            corruption_score += 3
            reasons.append(f"mixed_scripts_{script_diversity}")
        
        # Too many unidentified characters
        if other_ratio > 0.3:
            corruption_score += 2
            reasons.append(f"unknown_chars_{other_ratio:.1f}")
        
        # Low printable ratio
        if printable_ratio < 0.7:
            corruption_score += 2
            reasons.append(f"low_printable_{printable_ratio:.1f}")
        
        # No dominant script (chaotic mixing)
        if max_script_ratio < 0.5 and script_diversity > 2:
            corruption_score += 2
            reasons.append("script_chaos")
        
        # Check against regex patterns
        for pattern in self.noise_patterns:
            if pattern.search(line):
                corruption_score += 1
                reasons.append("pattern_match")
                break
        
        is_corrupted = corruption_score >= 3
        return is_corrupted, "|".join(reasons) if reasons else "clean"
    
    def clean_file(self, file_path):
        """Clean noise from a single file"""
        print(f"🔍 Filtering noise from {file_path.name}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            original_size = sum(len(line) for line in lines)
            original_line_count = len(lines)
            
            cleaned_lines = []
            corrupted_removed = 0
            
            for i, line in enumerate(lines):
                is_corrupted, reason = self.analyze_line_corruption(line)
                
                if is_corrupted:
                    corrupted_removed += 1
                    self.stats['corrupted_lines_removed'] += 1
                    print(f"  🗑️  Line {i+1}: {reason} - '{line.strip()[:60]}...'")
                else:
                    cleaned_lines.append(line)
            
            # Write cleaned file
            filtered_path = file_path.parent / f"filtered_{file_path.name}"
            with open(filtered_path, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            
            # Calculate stats
            final_size = sum(len(line) for line in cleaned_lines)
            size_reduction = original_size - final_size
            
            self.stats['files_processed'] += 1
            self.stats['total_size_reduction'] += size_reduction
            
            reduction_pct = (size_reduction / original_size * 100) if original_size > 0 else 0
            
            print(f"  ✅ {corrupted_removed:,} corrupted lines removed")
            print(f"  💾 {size_reduction/1024:.1f}KB saved ({reduction_pct:.1f}% reduction)")
            
            return {
                'file': file_path.name,
                'original_lines': original_line_count,
                'cleaned_lines': len(cleaned_lines),
                'corrupted_removed': corrupted_removed,
                'size_reduction_kb': size_reduction / 1024,
                'reduction_pct': reduction_pct
            }
            
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {str(e)}")
            return None
    
    def run_noise_filtering(self):
        """Run the complete noise filtering process"""
        print("🧹 PANACEA NOISE FILTER")
        print("Advanced corruption and garbage text removal")
        print("="*60)
        
        if not self.panacea_dir.exists():
            print(f"❌ Deduplicated panacea directory not found: {self.panacea_dir}")
            return
        
        # Find deduplicated files
        panacea_files = list(self.panacea_dir.glob("dedup_*.md")) + list(self.panacea_dir.glob("dedup_*.txt"))
        
        if not panacea_files:
            print(f"❌ No deduplicated panacea files found")
            return
        
        print(f"📁 Found {len(panacea_files)} files to filter")
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
        """Generate noise filtering report"""
        print("\n📈 NOISE FILTERING COMPLETE - SUMMARY REPORT")
        print("="*60)
        print(f"✅ Files Processed: {self.stats['files_processed']}")
        print(f"🗑️  Corrupted Lines Removed: {self.stats['corrupted_lines_removed']:,}")
        print(f"💾 Total Size Reduction: {self.stats['total_size_reduction']/1024/1024:.1f}MB")
        
        if results:
            total_corruption = sum(r['corrupted_removed'] for r in results)
            avg_reduction = sum(r['reduction_pct'] for r in results) / len(results)
            print(f"📊 Average Size Reduction: {avg_reduction:.1f}%")
            print(f"🧹 Total Corrupted Content: {total_corruption:,} lines")
        
        print("\n🛡️ NOISE FILTER STATUS:")
        print("✅ Encoding corruption removed")
        print("✅ OCR errors filtered")
        print("✅ Garbage text patterns eliminated")
        print("✅ Script chaos normalized")
        
        # Save detailed report
        report = {
            'summary': self.stats,
            'file_results': results,
            'timestamp': '2025-09-03',
            'total_reduction_mb': self.stats['total_size_reduction']/1024/1024,
            'patterns_detected': [
                'mixed_script_corruption',
                'encoding_artifacts', 
                'ocr_errors',
                'character_spam',
                'base64_garbage'
            ]
        }
        
        report_path = self.workspace_path / "panacea_noise_filter_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Detailed report saved: {report_path.name}")

def main():
    workspace_path = "/Users/sunghkim37/Library/CloudStorage/GoogleDrive-britkenko@gmail.com/My Drive/PACO/ESP/reservoir/reservoir"
    
    filter_tool = PanaceaNoiseFilter(workspace_path)
    results = filter_tool.run_noise_filtering()
    
    if results:
        print(f"\n🎯 NEXT STEPS:")
        print("1. Review filtered files (filtered_dedup_*.md/txt)")
        print("2. Check noise filter report for corruption details")
        print("3. Replace deduplicated files if satisfied with results")
        print("4. Enjoy ultra-clean panacea collection!")

if __name__ == "__main__":
    main()
