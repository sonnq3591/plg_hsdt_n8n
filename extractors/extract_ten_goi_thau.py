#!/usr/bin/env python3
"""
Extract Ten Goi Thau - Pure Content Extractor
Extracts 'ten_goi_thau' from TBMT.pdf and saves to master_data.json
"""

import os
import json
from pathlib import Path
import openai
import PyPDF2
from dotenv import load_dotenv
from datetime import datetime

class TenGoiThauExtractor:
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
        
        print(f"🎯 TenGoiThauExtractor initialized for batch: {self.batch_id}")
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

    def ask_openai_for_ten_goi_thau(self, tbmt_content):
        """Ask OpenAI to extract 'ten_goi_thau' from TBMT.pdf content - PRESERVED LOGIC"""
        prompt = f"""
Bạn là chuyên gia phân tích tài liệu đấu thầu Việt Nam.

Từ nội dung tài liệu TBMT (Thông báo mời thầu) dưới đây, hãy tìm và trích xuất CHÍNH XÁC tên gói thầu.

HƯỚNG DẪN CỤ THỂ:
Tên gói thầu nằm trong bảng "Thông tin gói thầu" hoặc tương tự, tại dòng có:
- Cột trái: "Tên gói thầu" (có thể viết là "Tên dự án", "Tên gói", "Package name")
- Cột phải: [TÊN GÓI THẦU THỰC TẾ]

Các cách viết có thể gặp:
- "Tên gói thầu" | "Chỉnh lý tài liệu..."
- "Tên dự án" | "Chỉnh lý tài liệu..."  
- "Package name" | "Chỉnh lý tài liệu..."
- "Tên gói" | "Chỉnh lý tài liệu..."

YÊU CẦU:
1. CHỈ lấy nội dung từ cột bên PHẢI của dòng "Tên gói thầu"
2. KHÔNG lấy từ tiêu đề tài liệu hoặc nơi khác
3. KHÔNG bao gồm mã số gói thầu
4. Trích xuất CHÍNH XÁC, giữ nguyên dấu câu tiếng Việt
5. Trả về CHỈ tên gói thầu, không giải thích

ĐỊNH DẠNG MONG ĐỢI:
Tìm cấu trúc bảng dạng:
```
| Tên gói thầu | [TÊN CẦN TRÍCH XUẤT] |
```

NỘI DUNG TBMT:
{tbmt_content}

TÊN GÓI THẦU (chỉ nội dung cột phải):"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Bạn là chuyên gia trích xuất thông tin từ bảng trong tài liệu đấu thầu Việt Nam. Chỉ trả về nội dung được yêu cầu từ cột cụ thể trong bảng."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.0
            )
            
            extracted_text = response.choices[0].message.content.strip()
            
            # Clean up any extra quotes or formatting
            if extracted_text.startswith('"') and extracted_text.endswith('"'):
                extracted_text = extracted_text[1:-1]
            
            print(f"🎯 OpenAI extracted from table: '{extracted_text}'")
            return extracted_text
            
        except Exception as e:
            print(f"❌ OpenAI API Error: {str(e)}")
            return "[KHÔNG TÌM THẤY]"

    def save_to_master_data(self, extracted_content):
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
        
        # Add/update ten_goi_thau data
        master_data["placeholders"]["ten_goi_thau"] = {
            "type": "simple_text",
            "content": extracted_content,
            "extracted_from": "TBMT.pdf",
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        # Update extraction log
        master_data["extraction_log"]["ten_goi_thau"] = {
            "status": "success" if extracted_content != "[KHÔNG TÌM THẤY]" else "failed",
            "timestamp": datetime.now().isoformat(),
            "source_file": "TBMT.pdf"
        }
        
        # Save updated master data
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved to master_data.json: {extracted_content}")
        
        # Also save individual file for debugging
        individual_file = self.extracted_dir / "ten_goi_thau.json"
        individual_data = {
            "content": extracted_content,
            "type": "simple_text",
            "extraction_timestamp": datetime.now().isoformat(),
            "source_file": "TBMT.pdf"
        }
        
        with open(individual_file, 'w', encoding='utf-8') as f:
            json.dump(individual_data, f, ensure_ascii=False, indent=2)
        
        return master_file

    def extract(self):
        """Main extraction function"""
        print("\n🎯 EXTRACTING: ten_goi_thau from TBMT.pdf")
        print("=" * 60)
        
        # Check if TBMT.pdf exists in current batch
        tbmt_file = self.pdfs_dir / "TBMT.pdf"
        if not tbmt_file.exists():
            print(f"❌ File not found: {tbmt_file}")
            print(f"📋 Available files: {list(self.pdfs_dir.glob('*.pdf'))}")
            
            # Log the failure
            self.save_extraction_failure("TBMT.pdf not found")
            return False
        
        # Extract text from TBMT.pdf
        print("📖 Reading TBMT.pdf...")
        tbmt_content = self.extract_text_from_pdf(tbmt_file)
        if not tbmt_content:
            self.save_extraction_failure("Failed to extract PDF text")
            return False
        
        print(f"✅ Extracted {len(tbmt_content)} characters from TBMT.pdf")
        
        # Show preview of content
        preview = tbmt_content[:500] + "..." if len(tbmt_content) > 500 else tbmt_content
        print(f"📄 Content preview:\n{preview}\n")
        
        # Ask OpenAI to extract ten_goi_thau
        print("🤖 Asking OpenAI to extract 'ten_goi_thau'...")
        ten_goi_thau = self.ask_openai_for_ten_goi_thau(tbmt_content)
        
        print(f"📝 Extracted 'ten_goi_thau': {ten_goi_thau}")
        
        # Save to master data
        master_file = self.save_to_master_data(ten_goi_thau)
        
        print(f"✅ SUCCESS: ten_goi_thau extracted and saved!")
        print(f"📄 Master data: {master_file}")
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
        master_data["extraction_log"]["ten_goi_thau"] = {
            "status": "failed",
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "source_file": "TBMT.pdf"
        }
        
        # Save updated master data
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)

def main():
    print("🇻🇳 Ten Goi Thau Extractor - Pure Content Extraction")
    print("=" * 70)
    
    try:
        # Initialize extractor
        extractor = TenGoiThauExtractor()
        print("✅ Extractor initialized successfully")
        
        # Extract ten_goi_thau
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