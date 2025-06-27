#!/usr/bin/env python3
"""
Extract Cac Buoc Thuc Hien - NEW Conditional Table Extractor
Extracts 'cac_buoc_thuc_hien' with step counting logic from CHUONG_V.pdf
"""

import os
import json
from pathlib import Path
import openai
import PyPDF2
from dotenv import load_dotenv
from datetime import datetime

class CacBuocExtractor:
    def __init__(self):
        """Initialize the extractor with batch-based folder structure"""
        # Set working directory to script's parent (BID_PROCESSOR)
        self.base_dir = Path(__file__).parent.parent
        os.chdir(self.base_dir)
        
        # Load environment variables
        load_dotenv()
        
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("❌ OPENAI_API_KEY not found in .env file!")
        
        openai.api_key = self.openai_api_key
        
        # Read current batch ID
        self.batch_id = self.read_batch_id()
        if not self.batch_id:
            raise ValueError("❌ No current batch ID found!")
        
        # Set up paths
        self.batch_dir = self.base_dir / self.batch_id
        self.pdfs_dir = self.batch_dir / "pdfs"
        self.extracted_dir = self.batch_dir / "extracted_data"
        self.templates_dir = self.base_dir / "templates"
        
        # Ensure directories exist
        self.extracted_dir.mkdir(exist_ok=True)
        
        print(f"🎯 CacBuocExtractor initialized for batch: {self.batch_id}")
        print(f"📁 PDFs source: {self.pdfs_dir}")
        print(f"📁 Templates: {self.templates_dir}")

    def read_batch_id(self):
        """Read current batch ID from current_batch.txt"""
        try:
            batch_file = self.base_dir / "current_batch.txt"
            with open(batch_file, "r") as f:
                batch_id = f.read().strip()
            print(f"📋 Current batch ID: {batch_id}")
            return batch_id
        except FileNotFoundError:
            print("❌ current_batch.txt not found!")
            return None

    def extract_text_from_pdf(self, pdf_path):
        """Extract text content from PDF file"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"❌ Error reading {pdf_path}: {str(e)}")
            return None

    def count_steps_in_chuong_v(self, chuong_v_content):
        """Count the number of steps in the process table from CHUONG_V.pdf"""
        prompt = f"""
From the CHUONG V document below, find the section about "Yêu cầu về quy trình chỉnh lý" or similar wording.

Look for a table that lists implementation steps. This table typically has:
- Step numbers (like 1, 2, 3, etc.)
- Process descriptions for each step
- The steps are usually numbered sequentially

Your task:
1. Find this process steps table
2. Count the TOTAL number of steps listed
3. The count should be either 21 or 23 steps

Return ONLY the number (21 or 23). If you can't find the table or the count is different, return "UNKNOWN".

CHUONG V CONTENT:
{chuong_v_content}

STEP COUNT:"""

        try:
            response = openai.ChatCompletion.create(
                model='gpt-4o',
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing Vietnamese document structures and counting process steps in tables. Return only the step count number."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.0
            )
            
            step_count_str = response.choices[0].message.content.strip()
            print(f"🔢 OpenAI detected step count: '{step_count_str}'")
            
            # Validate and convert to int
            if step_count_str in ["21", "23"]:
                return int(step_count_str)
            else:
                print(f"⚠️ Unexpected step count: {step_count_str}, defaulting to 21")
                return 21  # Default fallback
            
        except Exception as e:
            print(f"❌ OpenAI API Error: {str(e)}, defaulting to 21")
            return 21  # Default fallback

    def determine_source_file(self, step_count):
        """Determine which source file to use based on step count"""
        if step_count == 21:
            source_file = "21_BUOC.docx"
        elif step_count == 23:
            source_file = "23_BUOC.docx"
        else:
            print(f"⚠️ Unexpected step count {step_count}, defaulting to 21_BUOC.docx")
            source_file = "21_BUOC.docx"
        
        source_path = self.templates_dir / source_file
        
        if not source_path.exists():
            raise FileNotFoundError(f"❌ Source file not found: {source_path}")
        
        print(f"📄 Selected source file: {source_file}")
        return source_file

    def save_to_master_data(self, step_count, source_file):
        """Save extracted content to master_data.json"""
        master_file = self.extracted_dir / "master_data.json"
        
        # Load existing data or create new
        if master_file.exists():
            with open(master_file, 'r', encoding='utf-8') as f:
                master_data = json.load(f)
        else:
            master_data = {
                "batch_id": self.batch_id,
                "creation_timestamp": datetime.now().isoformat(),
                "placeholders": {},
                "extraction_log": {}
            }
        
        # Add/update cac_buoc_thuc_hien data
        master_data["placeholders"]["cac_buoc_thuc_hien"] = {
            "type": "table",
            "content": {
                "step_count": step_count,
                "source_file": source_file,
                "conditional_logic": True  # Flag for special handling
            },
            "extracted_from": "CHUONG_V.pdf",
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        # Update extraction log
        master_data["extraction_log"]["cac_buoc_thuc_hien"] = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "source_file": "CHUONG_V.pdf",
            "detected_steps": step_count,
            "selected_template": source_file
        }
        
        # Save updated master data
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved to master_data.json: {step_count} steps → {source_file}")
        
        # Also save individual file for debugging
        individual_file = self.extracted_dir / "cac_buoc_thuc_hien.json"
        individual_data = {
            "step_count": step_count,
            "source_file": source_file,
            "type": "table",
            "conditional_logic": True,
            "extraction_timestamp": datetime.now().isoformat(),
            "source_pdf": "CHUONG_V.pdf"
        }
        
        with open(individual_file, 'w', encoding='utf-8') as f:
            json.dump(individual_data, f, ensure_ascii=False, indent=2)
        
        return master_file

    def extract(self):
        """Main extraction function - NEW conditional table logic"""
        print("\n🎯 EXTRACTING: cac_buoc_thuc_hien from CHUONG_V.pdf")
        print("=" * 60)
        
        # Check if CHUONG_V.pdf exists in current batch
        chuong_v_file = self.pdfs_dir / "CHUONG_V.pdf"
        if not chuong_v_file.exists():
            print(f"❌ File not found: {chuong_v_file}")
            print(f"📋 Available files: {list(self.pdfs_dir.glob('*.pdf'))}")
            
            # Log the failure
            self.save_extraction_failure("CHUONG_V.pdf not found")
            return False
        
        # Step 1: Extract text from PDF
        print("📖 Step 1: Reading CHUONG_V.pdf...")
        chuong_v_content = self.extract_text_from_pdf(chuong_v_file)
        if not chuong_v_content:
            self.save_extraction_failure("Failed to extract PDF text")
            return False
        
        print(f"✅ Extracted {len(chuong_v_content)} characters")
        
        # Step 2: Count steps using AI
        print("🔢 Step 2: Counting process steps with AI...")
        step_count = self.count_steps_in_chuong_v(chuong_v_content)
        
        print(f"✅ Detected {step_count} steps")
        
        # Step 3: Determine source file
        print(f"📄 Step 3: Selecting template for {step_count} steps...")
        try:
            source_file = self.determine_source_file(step_count)
        except FileNotFoundError as e:
            self.save_extraction_failure(str(e))
            return False
        
        # Save to master data
        master_file = self.save_to_master_data(step_count, source_file)
        
        print(f"✅ SUCCESS: cac_buoc_thuc_hien extracted!")
        print(f"📄 Master data: {master_file}")
        print(f"📊 Steps: {step_count}, Template: {source_file}")
        return True

    def save_extraction_failure(self, error_message):
        """Save extraction failure to master_data.json"""
        master_file = self.extracted_dir / "master_data.json"
        
        # Load existing data or create new
        if master_file.exists():
            with open(master_file, 'r', encoding='utf-8') as f:
                master_data = json.load(f)
        else:
            master_data = {
                "batch_id": self.batch_id,
                "creation_timestamp": datetime.now().isoformat(),
                "placeholders": {},
                "extraction_log": {}
            }
        
        # Log the failure
        master_data["extraction_log"]["cac_buoc_thuc_hien"] = {
            "status": "failed",
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "source_file": "CHUONG_V.pdf"
        }
        
        # Save updated master data
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)

def main():
    print("🇻🇳 Cac Buoc Thuc Hien Extractor - NEW Conditional Table Extraction")
    print("=" * 70)
    
    try:
        # Initialize extractor
        extractor = CacBuocExtractor()
        print("✅ Extractor initialized successfully")
        
        # Extract cac_buoc_thuc_hien
        success = extractor.extract()
        
        if success:
            print("\n🎉 Extraction completed successfully!")
        else:
            print("\n❌ Extraction failed!")
            
    except ValueError as e:
        print(e)
        print("💡 Please ensure .env file exists with OPENAI_API_KEY")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()