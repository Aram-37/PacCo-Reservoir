#!/usr/bin/env python3
"""
PANACEA INTER-FILE CLEANER
Removes redundancies BETWEEN panacea files - cross-file duplicate detection and removal
"""

import os
import re
import json
import hashlib
from collections import defaultdict, Counter
from pathlib import Path
import difflib
from itertools import combinations

class PanaceaInterCleaner:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path)
        self.panacea_dir = self.workspace_path / "panacea"
        self.stats = {
            'files_analyzed': 0,
            'cross_file_duplicates': 0,
            'duplicate_blocks_removed': 0,
            'total_size_reduction': 0,
            'similarity_threshold': 0.8
        }
        
        # Store file contents and metadata
        self.file_data = {}
        self.paragraph_hashes = defaultdict(list)  # hash -> [(file, para_index)]
        self.sentence_hashes = defaultdict(list)   # hash -> [(file, sent_index)]
        
    def normalize_text(self, text):
        """Normalize text for comparison"""
        # Remove extra whitespace, normalize case
        text = re.sub(r'\s+', ' ', text.strip().lower())
        # Remove common markdown/formatting
        text = re.sub(r'[#*_`\-=]+', '', text)
        return text
    
    def get_text_hash(self, text):
        """Get hash of normalized text"""
        normalized = self.normalize_text(text)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def split_into_blocks(self, content):
        """Split content into paragraphs and sentences"""
        # Split by double newlines for paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Split by periods for sentences  
        sentences = []
        for para in paragraphs:
            para_sentences = [s.strip() for s in re.split(r'[.!?]+', para) if s.strip()]
            sentences.extend(para_sentences)
        
        return paragraphs, sentences
    
    def analyze_file(self, file_path):
        """Analyze a single file for content blocks"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Store original content
            self.file_data[file_path.name] = {
                'original_content': content,
                'size': len(content),
                'paragraphs': [],
                'sentences': []
            }
            
            paragraphs, sentences = self.split_into_blocks(content)
            
            # Hash paragraphs
            for i, para in enumerate(paragraphs):
                if len(para) > 50:  # Only check substantial paragraphs
                    para_hash = self.get_text_hash(para)
                    self.paragraph_hashes[para_hash].append((file_path.name, i, para))
                    self.file_data[file_path.name]['paragraphs'].append((i, para, para_hash))
            
            # Hash sentences
            for i, sent in enumerate(sentences):
                if len(sent) > 20:  # Only check substantial sentences
                    sent_hash = self.get_text_hash(sent)
                    self.sentence_hashes[sent_hash].append((file_path.name, i, sent))
                    self.file_data[file_path.name]['sentences'].append((i, sent, sent_hash))
                    
            print(f"📖 Analyzed {file_path.name}: {len(paragraphs)} paragraphs, {len(sentences)} sentences")
            
        except Exception as e:
            print(f"❌ Error analyzing {file_path.name}: {str(e)}")
    
    def find_cross_file_duplicates(self):
        """Find content that appears in multiple files"""
        duplicates = {
            'paragraphs': {},
            'sentences': {}
        }
        
        # Find paragraph duplicates
        for para_hash, occurrences in self.paragraph_hashes.items():
            if len(occurrences) > 1:  # Appears in multiple places
                files_involved = set(occ[0] for occ in occurrences)
                if len(files_involved) > 1:  # Across different files
                    duplicates['paragraphs'][para_hash] = occurrences
                    self.stats['cross_file_duplicates'] += 1
        
        # Find sentence duplicates
        for sent_hash, occurrences in self.sentence_hashes.items():
            if len(occurrences) > 1:
                files_involved = set(occ[0] for occ in occurrences)
                if len(files_involved) > 1:
                    duplicates['sentences'][sent_hash] = occurrences
        
        return duplicates
    
    def create_deduplicated_files(self, duplicates):
        """Create new files with cross-file duplicates removed"""
        
        # Track what to remove from each file
        removal_tracker = defaultdict(set)  # file -> set of hashes to remove
        
        # For each duplicate, keep only the first occurrence (in first file alphabetically)
        for para_hash, occurrences in duplicates['paragraphs'].items():
            # Sort by filename to get consistent "first" occurrence
            sorted_occurrences = sorted(occurrences, key=lambda x: x[0])
            keep_file = sorted_occurrences[0][0]
            
            # Mark for removal in all other files
            for filename, para_idx, para_text in sorted_occurrences[1:]:
                removal_tracker[filename].add(para_hash)
        
        # Create cleaned versions
        cleaned_files = {}
        total_size_reduction = 0
        
        for filename, file_info in self.file_data.items():
            original_content = file_info['original_content']
            original_size = len(original_content)
            
            # If no duplicates to remove, keep original
            if filename not in removal_tracker:
                cleaned_files[filename] = original_content
                continue
            
            # Remove duplicate paragraphs
            cleaned_paragraphs = []
            for para_idx, para_text, para_hash in file_info['paragraphs']:
                if para_hash not in removal_tracker[filename]:
                    cleaned_paragraphs.append(para_text)
                else:
                    self.stats['duplicate_blocks_removed'] += 1
            
            # Reconstruct content
            if cleaned_paragraphs:
                cleaned_content = '\n\n'.join(cleaned_paragraphs)
            else:
                # If all paragraphs removed, keep a minimal version
                cleaned_content = f"# {filename}\n\n[Content moved to other files to remove duplication]"
            
            cleaned_files[filename] = cleaned_content
            
            # Calculate size reduction
            size_reduction = original_size - len(cleaned_content)
            total_size_reduction += size_reduction
            
            if size_reduction > 0:
                reduction_pct = (size_reduction / original_size) * 100
                print(f"✂️  {filename}: {size_reduction/1024:.1f}KB removed ({reduction_pct:.1f}% reduction)")
        
        self.stats['total_size_reduction'] = total_size_reduction
        return cleaned_files
    
    def save_cleaned_files(self, cleaned_files):
        """Save the deduplicated files"""
        output_dir = self.panacea_dir / "deduplicated"
        output_dir.mkdir(exist_ok=True)
        
        for filename, content in cleaned_files.items():
            output_path = output_dir / f"dedup_{filename}"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"💾 Saved: {output_path.name}")
    
    def generate_duplicate_report(self, duplicates):
        """Generate detailed report of duplicates found"""
        report = {
            'summary': {
                'total_files_analyzed': self.stats['files_analyzed'],
                'cross_file_duplicates_found': self.stats['cross_file_duplicates'],
                'duplicate_blocks_removed': self.stats['duplicate_blocks_removed'],
                'total_size_reduction_kb': self.stats['total_size_reduction'] / 1024
            },
            'paragraph_duplicates': {},
            'sentence_duplicates': {}
        }
        
        # Document paragraph duplicates
        for para_hash, occurrences in duplicates['paragraphs'].items():
            files_involved = [occ[0] for occ in occurrences]
            sample_text = occurrences[0][2][:100] + "..." if len(occurrences[0][2]) > 100 else occurrences[0][2]
            
            report['paragraph_duplicates'][para_hash] = {
                'files': files_involved,
                'occurrences': len(occurrences),
                'sample_text': sample_text
            }
        
        # Document sentence duplicates  
        for sent_hash, occurrences in duplicates['sentences'].items():
            if len(occurrences) > 3:  # Only report frequently duplicated sentences
                files_involved = [occ[0] for occ in occurrences]
                sample_text = occurrences[0][2]
                
                report['sentence_duplicates'][sent_hash] = {
                    'files': files_involved,
                    'occurrences': len(occurrences),
                    'text': sample_text
                }
        
        # Save report
        report_path = self.workspace_path / "panacea_deduplication_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Deduplication report saved: {report_path.name}")
        return report
    
    def run_deduplication(self):
        """Run the complete inter-file deduplication process"""
        print("🔍 PANACEA INTER-FILE DEDUPLICATION")
        print("Cross-file redundancy detection and removal")
        print("="*60)
        
        if not self.panacea_dir.exists():
            print(f"❌ Panacea directory not found: {self.panacea_dir}")
            return
        
        # Find panacea files
        panacea_files = list(self.panacea_dir.glob("cleaned_*.md")) + list(self.panacea_dir.glob("cleaned_*.txt"))
        if not panacea_files:
            # Fall back to original files
            panacea_files = list(self.panacea_dir.glob("*.md")) + list(self.panacea_dir.glob("*.txt"))
        
        if not panacea_files:
            print(f"❌ No panacea files found")
            return
        
        print(f"📁 Analyzing {len(panacea_files)} files for cross-file duplicates")
        print("-"*60)
        
        # Step 1: Analyze all files
        for file_path in panacea_files:
            self.analyze_file(file_path)
            self.stats['files_analyzed'] += 1
        
        # Step 2: Find cross-file duplicates
        print("\n🔍 Detecting cross-file duplicates...")
        duplicates = self.find_cross_file_duplicates()
        
        # Step 3: Create deduplicated files
        print(f"\n✂️  Found {len(duplicates['paragraphs'])} duplicate paragraph blocks across files")
        print(f"✂️  Found {len(duplicates['sentences'])} duplicate sentence patterns across files")
        
        if duplicates['paragraphs'] or duplicates['sentences']:
            cleaned_files = self.create_deduplicated_files(duplicates)
            self.save_cleaned_files(cleaned_files)
            
            # Step 4: Generate report
            report = self.generate_duplicate_report(duplicates)
            
            print(f"\n📈 DEDUPLICATION COMPLETE:")
            print(f"✅ {self.stats['duplicate_blocks_removed']} duplicate blocks removed")
            print(f"💾 {self.stats['total_size_reduction']/1024:.1f}KB total size reduction")
            print(f"📁 Deduplicated files saved in: panacea/deduplicated/")
            
        else:
            print("✅ No cross-file duplicates found! Files are already well-deduplicated.")
        
        return duplicates

def main():
    workspace_path = "/Users/sunghkim37/Library/CloudStorage/GoogleDrive-britkenko@gmail.com/My Drive/PACO/ESP/reservoir/reservoir"
    
    cleaner = PanaceaInterCleaner(workspace_path)
    duplicates = cleaner.run_deduplication()
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Review deduplicated files in panacea/deduplicated/")
    print("2. Check deduplication report for details") 
    print("3. Replace original files if satisfied with results")
    print("4. Enjoy truly optimized panacea collection!")

if __name__ == "__main__":
    main()
