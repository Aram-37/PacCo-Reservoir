#!/usr/bin/env python3
"""
Panacea File Merger
Merges all text files in the Panacea folder, removing redundancies and organizing content
"""

import os
import glob
from pathlib import Path
import re
from collections import defaultdict, OrderedDict

class PanaceaFileMerger:
    def __init__(self, source_folder, output_file):
        self.source_folder = Path(source_folder)
        self.output_file = Path(output_file)
        self.content_sections = OrderedDict()
        self.seen_content = set()
        self.file_stats = {}
        
    def get_text_files(self):
        """Get all text files from the source folder"""
        extensions = ['*.txt', '*.md']  # Removed *.py to avoid processing the script itself
        text_files = []
        
        for ext in extensions:
            pattern = self.source_folder / ext
            text_files.extend(glob.glob(str(pattern)))
        
        # Filter out the script itself and any output files
        script_name = Path(__file__).name
        filtered_files = []
        for file_path in text_files:
            filename = Path(file_path).name
            if (filename != script_name and 
                not filename.startswith('MERGED_') and 
                not filename.startswith('merge_')):
                filtered_files.append(file_path)
            
        # Sort files to ensure consistent processing order
        return sorted(filtered_files)
    
    def normalize_content(self, content):
        """Normalize content for duplicate detection"""
        try:
            # Remove extra whitespace and normalize line endings
            normalized = re.sub(r'\s+', ' ', content.strip())
            # Remove common metadata patterns
            normalized = re.sub(r'# Lines \d+-\d+ from source', '', normalized)
            normalized = re.sub(r'## Dialogue Segment \d+', '', normalized)
            # Limit length to prevent memory issues
            if len(normalized) > 10000:
                normalized = normalized[:10000]
            return normalized.lower()
        except Exception as e:
            print(f"Error normalizing content: {e}")
            return ""
    
    def extract_sections(self, content, filename):
        """Extract meaningful sections from content"""
        sections = []
        
        # Split by common section markers
        section_patterns = [
            r'# ={20,}.*?={20,}',  # === Section Headers ===
            r'#{1,3}\s+[A-Z][^#\n]*',  # Markdown headers
            r'\*\*[^*]+\*\*:',  # Bold labels
            r'Label:',  # Dialogue labels
            r'Teacher:|Student:|AI:|Human:|Assistant:',  # Speaker labels
        ]
        
        current_section = []
        section_title = f"Content from {Path(filename).name}"
        
        lines = content.split('\n')
        for line in lines:
            # Check if line matches any section pattern
            is_section_start = False
            for pattern in section_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    if current_section:
                        sections.append({
                            'title': section_title,
                            'content': '\n'.join(current_section).strip(),
                            'source': filename
                        })
                    current_section = [line]
                    section_title = line.strip()
                    is_section_start = True
                    break
            
            if not is_section_start:
                current_section.append(line)
        
        # Add the last section
        if current_section:
            sections.append({
                'title': section_title,
                'content': '\n'.join(current_section).strip(),
                'source': filename
            })
        
        return sections
    
    def is_duplicate_content(self, content, min_similarity=0.8):
        """Check if content is duplicate based on similarity threshold"""
        try:
            normalized = self.normalize_content(content)
            
            if len(normalized) < 50:  # Too short to be meaningful
                return True
            
            # Create a hash for exact duplicates first
            content_hash = hash(normalized)
            if content_hash in self.seen_content:
                return True
                
            # Check against seen content for partial similarity
            normalized_words = set(normalized.split())
            if len(normalized_words) == 0:
                return True
                
            for seen in list(self.seen_content)[:100]:  # Limit comparison to last 100 items
                if isinstance(seen, str):
                    seen_words = set(seen.split())
                    if len(seen_words) == 0:
                        continue
                        
                    # Calculate simple similarity ratio
                    common_words = normalized_words & seen_words
                    total_words = normalized_words | seen_words
                    
                    if len(total_words) > 0:
                        similarity = len(common_words) / len(total_words)
                        if similarity > min_similarity:
                            return True
            
            self.seen_content.add(content_hash)
            return False
            
        except Exception as e:
            print(f"Error in duplicate detection: {e}")
            return False
    
    def categorize_content(self, sections):
        """Categorize content into logical groups"""
        categories = {
            'Core Principles': [],
            'Frameworks': [],
            'Methodologies': [],
            'Dialogues': [],
            'Guardian Architecture': [],
            'Processing Protocols': [],
            'Teaching Content': [],
            'Configuration': [],
            'Miscellaneous': []
        }
        
        for section in sections:
            title = section['title'].lower()
            content = section['content'].lower()
            
            # Categorize based on keywords
            if any(word in title for word in ['principle', 'core', 'foundation', 'immutable']):
                categories['Core Principles'].append(section)
            elif any(word in title for word in ['framework', 'structure', 'architecture']):
                categories['Frameworks'].append(section)
            elif any(word in title for word in ['methodology', 'protocol', 'process', 'imm', 'sarc']):
                categories['Methodologies'].append(section)
            elif any(word in title for word in ['dialogue', 'teacher', 'student', 'conversation']):
                categories['Dialogues'].append(section)
            elif any(word in title for word in ['guardian', 'mirego', 'sphinx', 'daemon']):
                categories['Guardian Architecture'].append(section)
            elif any(word in title for word in ['processing', 'engine', 'validation']):
                categories['Processing Protocols'].append(section)
            elif any(word in content for word in ['teach', 'learn', 'understanding', 'wisdom']):
                categories['Teaching Content'].append(section)
            elif any(word in title for word in ['config', 'setting', 'parameter']):
                categories['Configuration'].append(section)
            else:
                categories['Miscellaneous'].append(section)
        
        return categories
    
    def merge_files(self):
        """Main method to merge all files"""
        text_files = self.get_text_files()
        print(f"Found {len(text_files)} text files to process")
        
        all_sections = []
        
        # Process each file
        for file_path in text_files:
            try:
                print(f"Processing: {Path(file_path).name}...")
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                self.file_stats[file_path] = len(content)
                
                # Skip empty files
                if len(content.strip()) < 20:
                    print(f"  Skipped (too short): {Path(file_path).name}")
                    continue
                
                # Extract sections from the file
                sections = self.extract_sections(content, file_path)
                print(f"  Extracted {len(sections)} sections")
                
                # Filter out duplicates
                unique_sections = 0
                for section in sections:
                    if not self.is_duplicate_content(section['content']):
                        all_sections.append(section)
                        unique_sections += 1
                
                print(f"  Added {unique_sections} unique sections")
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        print(f"\nTotal unique sections collected: {len(all_sections)}")
        
        # Categorize all sections
        print("Categorizing content...")
        categorized = self.categorize_content(all_sections)
        
        # Generate merged output
        print("Generating merged file...")
        self.generate_merged_file(categorized)
        
        # Print statistics
        self.print_statistics(len(text_files), len(all_sections))
    
    def generate_merged_file(self, categorized_content):
        """Generate the final merged file"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("# COMPLETE FILE MERGE: All Text Files from Current Directory\n")
            f.write(f"## Generated from: {self.source_folder}\n")
            f.write(f"## Total files processed: {len(self.file_stats)}\n\n")
            
            f.write("---\n\n")
            
            # Write table of contents
            f.write("## TABLE OF CONTENTS\n\n")
            for category, sections in categorized_content.items():
                if sections:
                    f.write(f"- **{category}** ({len(sections)} sections)\n")
            f.write("\n---\n\n")
            
            # Write each category
            for category, sections in categorized_content.items():
                if not sections:
                    continue
                
                f.write(f"# {category.upper()}\n\n")
                
                for i, section in enumerate(sections, 1):
                    f.write(f"## {category} Section {i}: {section['title']}\n")
                    f.write(f"*Source: {Path(section['source']).name}*\n\n")
                    f.write(f"{section['content']}\n\n")
                    f.write("---\n\n")
            
            # Write file statistics
            f.write("# PROCESSING STATISTICS\n\n")
            f.write("## File Statistics:\n")
            for file_path, size in self.file_stats.items():
                f.write(f"- {Path(file_path).name}: {size} characters\n")
            f.write(f"\n## Total unique content sections: {sum(len(sections) for sections in categorized_content.values())}\n")
            f.write(f"## Duplicate sections removed: {len(self.seen_content) - sum(len(sections) for sections in categorized_content.values())}\n")
    
    def print_statistics(self, total_files, total_sections):
        """Print processing statistics"""
        print("\n" + "="*50)
        print("PROCESSING COMPLETE")
        print("="*50)
        print(f"Files processed: {total_files}")
        print(f"Total sections extracted: {total_sections}")
        print(f"Unique content sections: {sum(len(sections) for sections in self.content_sections.values()) if self.content_sections else total_sections}")
        print(f"Output file: {self.output_file}")
        print(f"Output size: {self.output_file.stat().st_size if self.output_file.exists() else 0} bytes")

def main():
    """Main execution function"""
    import sys
    
    # Use current directory where script is located
    script_dir = Path(__file__).parent
    source_folder = script_dir  # Current folder
    output_file = script_dir / "MERGED_FILES_COMPLETE.md"
    
    # Check if custom output file provided
    if len(sys.argv) > 1:
        output_file = script_dir / sys.argv[1]
    
    # Source folder is always the current directory
    if not source_folder.exists():
        print(f"Error: Current directory does not exist (this shouldn't happen)")
        return
    
    print(f"Merging files from current directory: {source_folder}")
    print(f"Output file: {output_file}")
    print("-" * 50)
    
    # Create merger and run
    merger = PanaceaFileMerger(source_folder, output_file)
    merger.merge_files()

if __name__ == "__main__":
    main()
