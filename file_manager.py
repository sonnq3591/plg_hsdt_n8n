#!/usr/bin/env python3
"""
PDF Mover for n8n
- Reads BatchID from current_batch.txt
- Creates batch_id/pdfs and batch_id/docx directories
- Moves all PDFs from temp/ to batch_id/pdfs/
"""

import os
import shutil
import glob

def move_pdfs():
    # Get current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Read BatchID from current_batch.txt
    batch_file = os.path.join(script_dir, "current_batch.txt")
    
    try:
        with open(batch_file, "r") as f:
            batch_id = f.read().strip()
        print(f"BatchID: {batch_id}")
    except FileNotFoundError:
        print("ERROR: current_batch.txt not found!")
        return False
    
    # Create directories
    batch_dir = os.path.join(script_dir, batch_id)
    pdfs_dir = os.path.join(batch_dir, "pdfs")
    docx_dir = os.path.join(batch_dir, "docx")
    temp_dir = os.path.join(script_dir, "temp")
    
    # Create batch directories
    os.makedirs(pdfs_dir, exist_ok=True)
    os.makedirs(docx_dir, exist_ok=True)
    print(f"Created: {batch_id}/pdfs/ and {batch_id}/docx/")
    
    # Check if temp exists
    if not os.path.exists(temp_dir):
        print("No temp directory found")
        return True
    
    # Find and move all PDF files
    pdf_files = glob.glob(os.path.join(temp_dir, "*.pdf"))
    moved_count = 0
    
    for pdf_file in pdf_files:
        filename = os.path.basename(pdf_file)
        destination = os.path.join(pdfs_dir, filename)
        
        try:
            shutil.move(pdf_file, destination)
            print(f"Moved: {filename}")
            moved_count += 1
        except Exception as e:
            print(f"Error moving {filename}: {e}")
    
    print(f"Total moved: {moved_count} files")
    return True

if __name__ == "__main__":
    move_pdfs()