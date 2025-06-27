#!/usr/bin/env python3
"""
Extract Muc Dich Cong Viec - Purpose Content Extractor
Extracts 'muc_dich_cong_viec' from CHUONG_V.pdf and saves to master_data.json
PRESERVES ALL ORIGINAL LOGIC from processor_muc_dich.py
"""

import os
import json
from pathlib import Path
import openai
import PyPDF2
from dotenv import load_dotenv
from datetime import datetime

class MucDichExtractor:
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
        
        print(f"🎯 MucDichExtractor initialized for batch: {self.batch_id}")
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
        """PRESERVED system prompt that excludes legal basis sections - EXACT COPY"""
        return """You are an assistant that extracts structured content related to "Mục đích" or "Mục đích Công việc" or similar wording from Vietnamese construction documents.

Your task is to:
- Intelligently identify the section that presents the content for "Mục đích" or "Mục đích Công việc" or similar wording, even if the section title is phrased differently.
- Extract its full content **without** modifying or summarizing anything.
- SKIP any section titles, headers, or sub-headers like "Mục đích công việc:", "Mục tiêu công việc:", "a) Mục đích:", etc.
- Start directly with the actual content paragraphs.
- **STOP extraction when you encounter legal basis sections** like "Căn cứ pháp lý", "Căn cứ Luật", "Quy định về", "Các Văn bản Luật", etc.

FORMAT STRICTLY as Markdown, following these rules:

1. **DO NOT include any leading section prefix** like 'c)', 'a.', '1)', etc.
2. **DO NOT include section headers** like "Mục đích công việc:", "Mục tiêu công việc:", etc.
3. **DO NOT include legal basis content** - stop before any "Căn cứ pháp lý" or similar sections.
4. The very first line (intro/statement) must NOT be bolded.
5. Only bold subheadings that are **followed by a list** (e.g. lines starting with '-').
6. Preserve all line breaks and paragraph groupings as they are in the original.
7. Every line (intro, subheading, and bullet) must be indented with **0.5 tab** (2 spaces).
8. Use dash '-' for bullet points and maintain their original text.
9. Do NOT paraphrase, summarize, reword, remove, or insert any content. Keep the original words exactly.
10. Extract ONLY the purpose/objective content, nothing about legal references or regulations."""

    def process_to_markdown(self, input_text):
        """PRESERVED Step 1: Extract and format to markdown"""
        system_prompt = self.create_system_prompt()
        markdown_output = self.format_text_markdown(input_text, system_prompt)
        
        # Save markdown for debugging
        debug_file = self.extracted_dir / 'muc_dich_cong_viec_debug.md'
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
        
        # Add/update muc_dich_cong_viec data
        master_data["placeholders"]["muc_dich_cong_viec"] = {
            "type": "structured_content",
            "content": structured_content,
            "raw_markdown": raw_markdown,  # Keep raw markdown for debugging
            "extracted_from": "CHUONG_V.pdf",
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        # Update extraction log
        success = structured_content is not None and len(structured_content) > 0
        master_data["extraction_log"]["muc_dich_cong_viec"] = {
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
        individual_file = self.extracted_dir / "muc_dich_cong_viec.json"
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
        print("\n🎯 EXTRACTING: muc_dich_cong_viec from CHUONG_V.pdf")
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
        input_file = self.extracted_dir / 'muc_dich_cong_viec_input.txt'
        input_file.write_text(chuong_v_content, encoding='utf-8')
        print(f"✅ Extracted {len(chuong_v_content)} characters")
        
        # Step 2: Process to markdown using PRESERVED logic
        print("🔄 Step 2: Processing purpose content to markdown...")
        markdown_content = self.process_to_markdown(chuong_v_content)
        
        print(f"📝 Raw markdown result: {markdown_content[:200]}...")
        
        if markdown_content == "[KHÔNG TÌM THẤY]" or not markdown_content.strip():
            print("❌ OpenAI returned empty or failed result")
            self.save_extraction_failure("OpenAI failed to extract purpose content")
            return False
        
        # Step 3: Parse markdown to structured data
        print("🔄 Step 3: Structuring markdown content...")
        structured_data = self.parse_markdown_to_structured_data(markdown_content)
        
        if not structured_data or len(structured_data) == 0:
            print("❌ Failed to parse markdown to structured data or empty result")
            self.save_extraction_failure("Failed to parse markdown to structured data")
            return False
        
        # Save to master data
        master_file = self.save_to_master_data(structured_data, markdown_content)
        
        print(f"✅ SUCCESS: muc_dich_cong_viec extracted and saved!")
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
        master_data["extraction_log"]["muc_dich_cong_viec"] = {
            "status": "failed",
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "source_file": "CHUONG_V.pdf"
        }
        
        # Save updated master data
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)

def main():
    print("🇻🇳 Muc Dich Cong Viec Extractor - Purpose Content Extraction")
    print("=" * 70)
    
    try:
        # Initialize extractor
        extractor = MucDichExtractor()
        print("✅ Extractor initialized successfully")
        
        # Extract muc_dich_cong_viec
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