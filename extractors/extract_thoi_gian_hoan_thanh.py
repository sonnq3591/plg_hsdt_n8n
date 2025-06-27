#!/usr/bin/env python3
"""
Extract Thoi Gian Hoan Thanh - NEW Simple Text Extractor
Extracts 'thoi_gian_hoan_thanh' (completion time) from CHUONG_III.pdf
"""

import os
import json
from pathlib import Path
import openai
import PyPDF2
from dotenv import load_dotenv
from datetime import datetime

class ThoiGianHoanThanhExtractor:
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
        
        print(f"🎯 ThoiGianHoanThanhExtractor initialized for batch: {self.batch_id}")

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

    def ask_openai_for_thoi_gian_hoan_thanh(self, pdf_content):
        """Ask OpenAI to extract completion time from CHUONG_III.pdf"""
        prompt = f"""
Bạn là chuyên gia phân tích tài liệu CHUONG III Việt Nam.

Từ nội dung tài liệu CHUONG III dưới đây, hãy tìm và trích xuất CHÍNH XÁC thời gian hoàn thành.

HƯỚNG DẪN CỤ THỂ:
Tìm trong bảng/danh sách các yêu cầu có dòng về:
- "Thời gian hoàn thành" 
- "Tiến độ thực hiện"
- "Thời hạn hoàn thành"
- hoặc từ khóa tương tự

Thường có cấu trúc:
```
6.1 | Thời gian hoàn thành | ≤ 120 ngày | Đạt
```

YÊU CẦU:
1. CHỈ trích xuất thời gian (như "120 ngày", "3 tháng", "90 ngày")
2. LOẠI BỎ tất cả ký hiệu toán học (≤, ≥, <, >, =)
3. CHỈ lấy số và đơn vị thời gian
4. KHÔNG lấy từ cột "Đạt/Không đạt"
5. Trả về CHỈ thời gian thuần túy, không giải thích

VÍ DỤ:
- Nếu thấy "≤ 120 ngày" → trả về "120 ngày"
- Nếu thấy "> 3 tháng" → trả về "3 tháng"

NỘI DUNG CHUONG III:
{pdf_content}

THỜI GIAN HOÀN THÀNH (chỉ số và đơn vị):"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Bạn là chuyên gia trích xuất thời gian hoàn thành từ tài liệu CHUONG III Việt Nam. Chỉ trả về giá trị thời gian."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.0
            )
            
            extracted_text = response.choices[0].message.content.strip()
            
            # Clean up any extra quotes or formatting
            if extracted_text.startswith('"') and extracted_text.endswith('"'):
                extracted_text = extracted_text[1:-1]
            
            print(f"🎯 OpenAI extracted thoi_gian_hoan_thanh: '{extracted_text}'")
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
        
        # Add/update thoi_gian_hoan_thanh data
        master_data["placeholders"]["thoi_gian_hoan_thanh"] = {
            "type": "simple_text",
            "content": extracted_content,
            "extracted_from": "CHUONG_III.pdf",
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        # Update extraction log
        master_data["extraction_log"]["thoi_gian_hoan_thanh"] = {
            "status": "success" if extracted_content != "[KHÔNG TÌM THẤY]" else "failed",
            "timestamp": datetime.now().isoformat(),
            "source_file": "CHUONG_III.pdf"
        }
        
        # Save updated master data
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved to master_data.json: {extracted_content}")
        return master_file

    def extract(self):
        """Main extraction function"""
        print("\n🎯 EXTRACTING: thoi_gian_hoan_thanh from CHUONG_III.pdf")
        print("=" * 60)
        
        # Check if CHUONG_III.pdf exists in current batch
        chuong_iii_file = self.pdfs_dir / "CHUONG_III.pdf"
        if not chuong_iii_file.exists():
            print(f"❌ File not found: {chuong_iii_file}")
            print(f"📋 Available files: {list(self.pdfs_dir.glob('*.pdf'))}")
            return False
        
        # Extract text from CHUONG_III.pdf
        print("📖 Reading CHUONG_III.pdf...")
        chuong_iii_content = self.extract_text_from_pdf(chuong_iii_file)
        if not chuong_iii_content:
            return False
        
        print(f"✅ Extracted {len(chuong_iii_content)} characters from CHUONG_III.pdf")
        
        # Ask OpenAI to extract thoi_gian_hoan_thanh
        print("🤖 Asking OpenAI to extract completion time...")
        thoi_gian_hoan_thanh = self.ask_openai_for_thoi_gian_hoan_thanh(chuong_iii_content)
        
        print(f"📝 Extracted completion time: {thoi_gian_hoan_thanh}")
        
        # Save to master data
        master_file = self.save_to_master_data(thoi_gian_hoan_thanh)
        
        print(f"✅ SUCCESS: thoi_gian_hoan_thanh extracted and saved!")
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
        master_data["extraction_log"]["thoi_gian_hoan_thanh"] = {
            "status": "failed",
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "source_file": "CHUONG_III.pdf"
        }
        
        # Save updated master data
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)

def main():
    print("🇻🇳 Thoi Gian Hoan Thanh Extractor - Completion Time Extraction")
    print("=" * 70)
    
    try:
        # Initialize extractor
        extractor = ThoiGianHoanThanhExtractor()
        print("✅ Extractor initialized successfully")
        
        # Extract thoi_gian_hoan_thanh
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