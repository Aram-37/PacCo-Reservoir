#!/usr/bin/env python3
"""
File Chunker Script
Splits large files into smaller chunks based on user-specified size
"""

import os
import math
from pathlib import Path

def get_file_size_mb(file_path):
    """Get file size in MB"""
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    return size_mb

def chunk_file(file_path, chunk_size_mb):
    """Split file into chunks of specified size"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"Error: File '{file_path}' does not exist!")
        return False
    
    # Calculate chunk size in bytes
    chunk_size_bytes = int(chunk_size_mb * 1024 * 1024)
    
    # Get file info
    file_size_bytes = file_path.stat().st_size
    file_size_mb = file_size_bytes / (1024 * 1024)
    total_chunks = math.ceil(file_size_bytes / chunk_size_bytes)
    
    print(f"\nFile Information:")
    print(f"File: {file_path.name}")
    print(f"Size: {file_size_mb:.2f} MB ({file_size_bytes:,} bytes)")
    print(f"Chunk size: {chunk_size_mb} MB ({chunk_size_bytes:,} bytes)")
    print(f"Total chunks to create: {total_chunks}")
    
    # Create output directory
    output_dir = file_path.parent / f"{file_path.stem}_chunks"
    output_dir.mkdir(exist_ok=True)
    
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    try:
        with open(file_path, 'rb') as input_file:
            chunk_num = 1
            
            while True:
                # Read chunk
                chunk_data = input_file.read(chunk_size_bytes)
                
                if not chunk_data:
                    break
                
                # Create chunk filename
                chunk_filename = f"{file_path.stem}_chunk_{chunk_num:03d}{file_path.suffix}"
                chunk_path = output_dir / chunk_filename
                
                # Write chunk
                with open(chunk_path, 'wb') as chunk_file:
                    chunk_file.write(chunk_data)
                
                chunk_size_actual = len(chunk_data) / (1024 * 1024)
                print(f"Created: {chunk_filename} ({chunk_size_actual:.2f} MB)")
                
                chunk_num += 1
        
        print("-" * 50)
        print(f"✅ Successfully created {chunk_num - 1} chunks")
        print(f"📁 Chunks saved in: {output_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error chunking file: {e}")
        return False

def chunk_text_file_by_lines(file_path, lines_per_chunk):
    """Split text file by number of lines (alternative method for text files)"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"Error: File '{file_path}' does not exist!")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        total_chunks = math.ceil(total_lines / lines_per_chunk)
        
        print(f"\nText File Information:")
        print(f"File: {file_path.name}")
        print(f"Total lines: {total_lines:,}")
        print(f"Lines per chunk: {lines_per_chunk:,}")
        print(f"Total chunks to create: {total_chunks}")
        
        # Create output directory
        output_dir = file_path.parent / f"{file_path.stem}_line_chunks"
        output_dir.mkdir(exist_ok=True)
        
        print(f"Output directory: {output_dir}")
        print("-" * 50)
        
        for chunk_num in range(total_chunks):
            start_line = chunk_num * lines_per_chunk
            end_line = min((chunk_num + 1) * lines_per_chunk, total_lines)
            
            chunk_lines = lines[start_line:end_line]
            
            # Create chunk filename
            chunk_filename = f"{file_path.stem}_lines_{chunk_num + 1:03d}{file_path.suffix}"
            chunk_path = output_dir / chunk_filename
            
            # Write chunk
            with open(chunk_path, 'w', encoding='utf-8') as chunk_file:
                chunk_file.writelines(chunk_lines)
            
            actual_lines = len(chunk_lines)
            print(f"Created: {chunk_filename} ({actual_lines:,} lines)")
        
        print("-" * 50)
        print(f"✅ Successfully created {total_chunks} chunks")
        print(f"📁 Chunks saved in: {output_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error chunking text file: {e}")
        return False

def list_files_in_directory():
    """List files in current directory for user selection"""
    current_dir = Path.cwd()
    files = [f for f in current_dir.iterdir() if f.is_file() and not f.name.startswith('.')]
    
    if not files:
        print("No files found in current directory.")
        return []
    
    print("\nFiles in current directory:")
    print("-" * 50)
    for i, file_path in enumerate(files, 1):
        size_mb = get_file_size_mb(file_path)
        print(f"{i:2d}. {file_path.name} ({size_mb:.2f} MB)")
    
    return files

def get_user_input():
    """Get user input for file selection and chunk size"""
    print("🔧 File Chunker Tool")
    print("=" * 50)
    
    # List available files
    files = list_files_in_directory()
    if not files:
        return None, None, None
    
    # Get file selection
    while True:
        try:
            choice = input(f"\nSelect file number (1-{len(files)}) or enter file path: ").strip()
            
            if choice.isdigit():
                file_index = int(choice) - 1
                if 0 <= file_index < len(files):
                    selected_file = files[file_index]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(files)}")
            else:
                # User entered a file path
                selected_file = Path(choice)
                if selected_file.exists():
                    break
                else:
                    print(f"File '{choice}' does not exist. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or file path.")
    
    print(f"\nSelected file: {selected_file.name}")
    print(f"File size: {get_file_size_mb(selected_file):.2f} MB")
    
    # Check if it's a text file for line-based chunking option
    is_text_file = selected_file.suffix.lower() in ['.txt', '.md', '.csv', '.log', '.json', '.xml', '.html']
    
    if is_text_file:
        print("\n📝 Text file detected!")
        chunk_method = input("Chunk by (s)ize or (l)ines? [s/l]: ").strip().lower()
        if chunk_method == 'l':
            # Lines-based chunking
            while True:
                try:
                    lines_per_chunk = int(input("Enter lines per chunk: "))
                    if lines_per_chunk > 0:
                        return selected_file, None, lines_per_chunk
                    else:
                        print("Please enter a positive number.")
                except ValueError:
                    print("Please enter a valid number.")
    
    # Size-based chunking
    while True:
        try:
            chunk_size = float(input("Enter chunk size in MB: "))
            if chunk_size > 0:
                return selected_file, chunk_size, None
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")

def main():
    """Main execution function"""
    file_path, chunk_size_mb, lines_per_chunk = get_user_input()
    
    if file_path is None:
        return
    
    print("\n🚀 Starting file chunking...")
    
    if lines_per_chunk:
        # Line-based chunking
        success = chunk_text_file_by_lines(file_path, lines_per_chunk)
    else:
        # Size-based chunking
        success = chunk_file(file_path, chunk_size_mb)
    
    if success:
        print("\n✨ Chunking completed successfully!")
    else:
        print("\n💥 Chunking failed!")

if __name__ == "__main__":
    main()
