#!/usr/bin/env python3
"""
Extract Pham Vi Cung Cap - Pure Content Extractor
Extracts table data from BMMT.pdf and saves to master_data.json
"""

import os
import json
from pathlib import Path
import openai
import PyPDF2
from dotenv import load_dotenv
from datetime import datetime
import csv
from io import StringIO

class PhamViExtractor:
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
        
        # Ensure directories exist
        self.extracted_dir.mkdir(exist_ok=True)
        
        print(f"🎯 PhamViExtractor initialized for batch: {self.batch_id}")
        print(f"📁 PDFs source: {self.pdfs_dir}")
        print(f"📁 Extracted data: {self.extracted_dir}")

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
        """Extract text content from PDF file - PRESERVED LOGIC"""
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

    def extract_table_from_bmmt(self, bmmt_content):
        """Extract table data from BMMT content - PRESERVED LOGIC"""
        prompt = f"""
From the BMMT document below, find the main service scope table and extract it with these EXACT columns only:

1. STT (sequential number)
2. Danh mục dịch vụ (service category/name)
3. Khối lượng (quantity/volume - KEEP EXACT FORMAT from PDF including commas/dots like "33,81" or "182,31")
4. Đơn vị tính (unit - like "Mét")  
5. Địa điểm thực hiện (implementation location - the full address)
6. Ngày hoàn thành (completion date - like "120 ngày")

CRITICAL FORMATTING RULES:
- For "Khối lượng" column: PRESERVE the exact number format from the original PDF
- If the PDF shows "33,81" keep it as "33,81" (with comma)
- If the PDF shows "182,31" keep it as "182,31" (with comma)
- Do NOT convert to decimals like "33.81" - keep the original Vietnamese number format
- SKIP the "Mô tả dịch vụ" column completely
- Keep all other Vietnamese text exactly as written

Use CSV format but put the Khối lượng numbers in quotes to preserve formatting:
STT,Danh mục dịch vụ,Khối lượng,Đơn vị tính,Địa điểm thực hiện,Ngày hoàn thành
1,"Service name 1","33,81",Mét,"Full address...","120 ngày"
2,"Service name 2","182,31",Mét,"Full address...","120 ngày"

BMMT CONTENT:
{bmmt_content}

CSV TABLE (preserve exact number formats):
"""

        try:
            response = openai.ChatCompletion.create(
                model='gpt-4o',
                messages=[
                    {"role": "system", "content": "You are an expert at extracting Vietnamese tables while preserving exact number formatting. Never change comma/dot formatting in numbers - keep them exactly as they appear in the original document."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.0
            )
            
            csv_data = response.choices[0].message.content.strip()
            
            # Clean up the CSV data - PRESERVED LOGIC
            lines = csv_data.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('```'):
                    cleaned_lines.append(line)
            
            final_csv = '\n'.join(cleaned_lines)
            print(f"🎯 OpenAI extracted table with {len(cleaned_lines)} rows (preserving number formats)")
            
            # Verify column count and show sample - PRESERVED LOGIC
            if cleaned_lines:
                first_row = cleaned_lines[0]
                reader = csv.reader(StringIO(first_row))
                cols = next(reader)
                print(f"📊 Header columns: {cols}")
                if len(cols) != 6:
                    print(f"⚠️ Warning: Expected 6 columns, got {len(cols)}")
                
                # Show first data row to verify number formatting
                if len(cleaned_lines) > 1:
                    data_row = cleaned_lines[1]
                    reader = csv.reader(StringIO(data_row))
                    data = next(reader)
                    if len(data) >= 3:
                        print(f"📊 Sample Khối lượng value: '{data[2]}' (should preserve commas/dots)")
            
            return final_csv
            
        except Exception as e:
            print(f"❌ OpenAI API Error: {str(e)}")
            return None

    def parse_csv_to_structured_data(self, csv_data):
        """Parse CSV data into structured format for JSON storage"""
        try:
            lines = csv_data.strip().splitlines()
            if not lines:
                return None
            
            # Parse CSV
            parsed_rows = []
            for i, line in enumerate(lines):
                if line.strip():
                    try:
                        reader = csv.reader(StringIO(line))
                        row = next(reader)
                        parsed_rows.append(row)
                    except Exception as e:
                        print(f"⚠️ Error parsing line {i}: {e}")
                        continue
            
            if not parsed_rows:
                return None
            
            # Structure: headers + rows
            headers = parsed_rows[0]
            rows = parsed_rows[1:] if len(parsed_rows) > 1 else []
            
            structured_data = {
                "headers": headers,
                "rows": rows,
                "total_rows": len(rows)
            }
            
            print(f"📊 Structured table: {len(headers)} columns, {len(rows)} data rows")
            return structured_data
            
        except Exception as e:
            print(f"❌ Error structuring CSV data: {str(e)}")
            return None

    def save_to_master_data(self, structured_table_data, raw_csv):
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
        
        # Add/update pham_vi_cung_cap data
        master_data["placeholders"]["pham_vi_cung_cap"] = {
            "type": "table",
            "content": structured_table_data,
            "raw_csv": raw_csv,  # Keep raw CSV for debugging
            "extracted_from": "BMMT.pdf",
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        # Update extraction log
        success = structured_table_data is not None
        master_data["extraction_log"]["pham_vi_cung_cap"] = {
            "status": "success" if success else "failed",
            "timestamp": datetime.now().isoformat(),
            "source_file": "BMMT.pdf",
            "rows_extracted": structured_table_data.get("total_rows", 0) if success else 0
        }
        
        # Save updated master data
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved to master_data.json: {structured_table_data.get('total_rows', 0)} rows")
        
        # Also save individual file for debugging
        individual_file = self.extracted_dir / "pham_vi_cung_cap.json"
        individual_data = {
            "content": structured_table_data,
            "raw_csv": raw_csv,
            "type": "table",
            "extraction_timestamp": datetime.now().isoformat(),
            "source_file": "BMMT.pdf"
        }
        
        with open(individual_file, 'w', encoding='utf-8') as f:
            json.dump(individual_data, f, ensure_ascii=False, indent=2)
        
        # Save raw CSV for debugging
        csv_file = self.extracted_dir / "pham_vi_cung_cap.csv"
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(raw_csv)
        
        return master_file

    def extract(self):
        """Main extraction function"""
        print("\n🎯 EXTRACTING: pham_vi_cung_cap from BMMT.pdf")
        print("=" * 60)
        
        # Check if BMMT.pdf exists in current batch
        bmmt_file = self.pdfs_dir / "BMMT.pdf"
        if not bmmt_file.exists():
            print(f"❌ File not found: {bmmt_file}")
            print(f"📋 Available files: {list(self.pdfs_dir.glob('*.pdf'))}")
            
            # Log the failure
            self.save_extraction_failure("BMMT.pdf not found")
            return False
        
        # Extract text from BMMT.pdf
        print("📖 Reading BMMT.pdf...")
        bmmt_content = self.extract_text_from_pdf(bmmt_file)
        if not bmmt_content:
            self.save_extraction_failure("Failed to extract PDF text")
            return False
        
        print(f"✅ Extracted {len(bmmt_content)} characters from BMMT.pdf")
        
        # Extract table as CSV
        print("📊 Extracting table from BMMT...")
        csv_data = self.extract_table_from_bmmt(bmmt_content)
        
        if not csv_data:
            self.save_extraction_failure("Failed to extract table with OpenAI")
            return False
        
        # Parse CSV to structured data
        print("🔄 Structuring table data...")
        structured_data = self.parse_csv_to_structured_data(csv_data)
        
        if not structured_data:
            self.save_extraction_failure("Failed to parse extracted CSV")
            return False
        
        # Save to master data
        master_file = self.save_to_master_data(structured_data, csv_data)
        
        print(f"✅ SUCCESS: pham_vi_cung_cap extracted and saved!")
        print(f"📄 Master data: {master_file}")
        print(f"📊 Table: {structured_data['total_rows']} rows, {len(structured_data['headers'])} columns")
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
        master_data["extraction_log"]["pham_vi_cung_cap"] = {
            "status": "failed",
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "source_file": "BMMT.pdf"
        }
        
        # Save updated master data
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)

def main():
    print("🇻🇳 Pham Vi Cung Cap Extractor - Pure Table Extraction")
    print("=" * 70)
    
    try:
        # Initialize extractor
        extractor = PhamViExtractor()
        print("✅ Extractor initialized successfully")
        
        # Extract pham_vi_cung_cap
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