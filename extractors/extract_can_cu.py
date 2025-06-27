#!/usr/bin/env python3
"""
Extract Can Cu Phap Ly - Legal Basis Content Extractor
Extracts 'can_cu_phap_ly' from CHUONG_V.pdf and saves to master_data.json
PRESERVES ALL ORIGINAL LOGIC from processor_can_cu.py
"""

import os
import json
from pathlib import Path
import openai
import PyPDF2
from dotenv import load_dotenv
from datetime import datetime

class CanCuExtractor:
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
        
        print(f"🎯 CanCuExtractor initialized for batch: {self.batch_id}")
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

    def format_text_markdown(self, input_text, system_prompt):
        """PRESERVED OpenAI formatting function from original processor"""
        try:
            response = openai.ChatCompletion.create(
                model='gpt-4o',
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": input_text}
                ],
                max_tokens=1500,
                temperature=0.0
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ OpenAI API Error: {str(e)}")
            return "[KHÔNG TÌM THẤY]"

    def create_system_prompt(self):
        """PRESERVED system prompt for legal basis extraction - EXACT COPY"""
        return """You are an expert in formatting administrative and archival documents into clean, professional Markdown.
Your job is to format the text clearly while preserving all original content and structure exactly as written.
🚫 Never insert or generate any additional title, subheading, summary, or restructuring of the original input.
You are not allowed to add content. Only apply formatting (like bolding or bulleting) to text that already exists in the input.

EXTRACTION TASK: Extract content related to "Căn cứ pháp lý" or legal basis sections from Vietnamese construction documents.

Instructions:
- Find and extract sections with legal document listings and regulations
- SKIP section headers like "c) Công tác chỉnh lý...", "3. Căn cứ pháp lý", "Căn cứ pháp lý", etc.
- START directly with the document group headings (like "Các Văn bản Luật, Nghị định về...")
- Preserve 100% of the original text exactly as written (except section headers).
- Do not remove, summarize, reword, or rearrange any line.
- Maintain all punctuation and line order from the source.
- Apply formatting only where clearly required:

🔹 Bold subheadings that introduce grouped documents:
Use **...** to bold a line only if all the following are true:
- The line is on its own (not part of a sentence or paragraph)
- It is short (ideally under 20 words)
- It introduces a group of official/legal/administrative documents
- It is followed by bullet points (-) listing specific documents or policies

✅ Example — these should be bolded:
**Các Văn bản Luật, Nghị định về công tác lưu trữ:**
**Quy định về thời hạn bảo quản tài liệu:**
**Quy định về các bước của nghiệp vụ chỉnh lý tài liệu:**
**Quy định về tiêu chuẩn kỹ thuật văn phòng phẩm:**

🚫 Do NOT bold narrative or sentence-style lines
🚫 Do NOT include section prefixes like "c)", "3.", etc.
🚫 Do NOT include introductory sentences like "Công tác chỉnh lý tài liệu áp dụng căn cứ vào..."

🔹 Bullet points:
- Use - to list individual documents exactly as written
- Preserve punctuation, spelling, accents, and spacing from the original
- Do not insert or reorder any line

Line breaks:
- Keep original paragraph breaks as in the source
- Only insert new lines if:
  - A bullet list is clearly introduced
  - A section visually begins a new paragraph in the original

Markdown formatting:
- Use only valid, clean Markdown:
- Use - for bullets
- Use **...** for bold subheadings
- No extra symbols, no HTML, and no interpretation

Start extraction from the first document group heading, not from section headers or introductory text."""

    def process_to_markdown(self, input_text):
        """PRESERVED Step 1: Extract and format to markdown"""
        system_prompt = self.create_system_prompt()
        markdown_output = self.format_text_markdown(input_text, system_prompt)
        
        # Save markdown for debugging
        debug_file = self.extracted_dir / 'can_cu_phap_ly_debug.md'
        debug_file.write_text(markdown_output, encoding='utf-8')
        print(f"✅ Saved debug markdown: {debug_file}")
        
        return markdown_output

    def parse_markdown_to_structured_data(self, markdown_content):
        """Parse markdown into structured format for JSON storage"""
        try:
            lines = markdown_content.strip().splitlines()
            if not lines:
                return None
            
            structured_content = []
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for bold headings
                if line.startswith('**') and line.endswith('**'):
                    heading_text = line[2:-2]  # Remove ** markers
                    current_section = {
                        "type": "heading",
                        "text": heading_text,
                        "level": 1,
                        "items": []
                    }
                    structured_content.append(current_section)
                    
                # Check for bullet points
                elif line.startswith('- '):
                    bullet_text = line[2:].strip()  # Remove "- " prefix
                    if current_section:
                        current_section["items"].append(bullet_text)
                    else:
                        # Bullet without section - create standalone
                        structured_content.append({
                            "type": "bullet_item",
                            "text": bullet_text
                        })
                        
                # Regular paragraph
                else:
                    structured_content.append({
                        "type": "paragraph",
                        "text": line
                    })
            
            print(f"📊 Structured content: {len(structured_content)} sections")
            return structured_content
            
        except Exception as e:
            print(f"❌ Error structuring markdown: {str(e)}")
            return None

    def save_to_master_data(self, structured_content, raw_markdown):
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
        
        # Add/update can_cu_phap_ly data
        master_data["placeholders"]["can_cu_phap_ly"] = {
            "type": "structured_content",
            "content": structured_content,
            "raw_markdown": raw_markdown,  # Keep raw markdown for debugging
            "extracted_from": "CHUONG_V.pdf",
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        # Update extraction log
        success = structured_content is not None and len(structured_content) > 0
        master_data["extraction_log"]["can_cu_phap_ly"] = {
            "status": "success" if success else "failed",
            "timestamp": datetime.now().isoformat(),
            "source_file": "CHUONG_V.pdf",
            "sections_extracted": len(structured_content) if success else 0
        }
        
        # Save updated master data
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved to master_data.json: {len(structured_content) if structured_content else 0} sections")
        
        # Also save individual file for debugging
        individual_file = self.extracted_dir / "can_cu_phap_ly.json"
        individual_data = {
            "content": structured_content,
            "raw_markdown": raw_markdown,
            "type": "structured_content",
            "extraction_timestamp": datetime.now().isoformat(),
            "source_file": "CHUONG_V.pdf"
        }
        
        with open(individual_file, 'w', encoding='utf-8') as f:
            json.dump(individual_data, f, ensure_ascii=False, indent=2)
        
        return master_file

    def extract(self):
        """Main extraction function - PRESERVED LOGIC"""
        print("\n🎯 EXTRACTING: can_cu_phap_ly from CHUONG_V.pdf")
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
        
        # Save input text for debugging
        input_file = self.extracted_dir / 'can_cu_phap_ly_input.txt'
        input_file.write_text(chuong_v_content, encoding='utf-8')
        print(f"✅ Extracted {len(chuong_v_content)} characters")
        
        # Step 2: Process to markdown using PRESERVED logic
        print("🔄 Step 2: Processing legal basis to markdown...")
        markdown_content = self.process_to_markdown(chuong_v_content)
        
        if markdown_content == "[KHÔNG TÌM THẤY]":
            self.save_extraction_failure("OpenAI failed to extract legal basis")
            return False
        
        # Step 3: Parse markdown to structured data
        print("🔄 Step 3: Structuring markdown content...")
        structured_data = self.parse_markdown_to_structured_data(markdown_content)
        
        if not structured_data:
            self.save_extraction_failure("Failed to parse markdown to structured data")
            return False
        
        # Save to master data
        master_file = self.save_to_master_data(structured_data, markdown_content)
        
        print(f"✅ SUCCESS: can_cu_phap_ly extracted and saved!")
        print(f"📄 Master data: {master_file}")
        print(f"📊 Structured data: {len(structured_data)} sections")
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
        master_data["extraction_log"]["can_cu_phap_ly"] = {
            "status": "failed",
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "source_file": "CHUONG_V.pdf"
        }
        
        # Save updated master data
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)

def main():
    print("🇻🇳 Can Cu Phap Ly Extractor - Legal Basis Content Extraction")
    print("=" * 70)
    
    try:
        # Initialize extractor
        extractor = CanCuExtractor()
        print("✅ Extractor initialized successfully")
        
        # Extract can_cu_phap_ly
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