#!/usr/bin/env python3
"""
Document Generator - FIXED with Hybrid Replacement Logic
Combines run-level replacement for simple text with your proven paragraph replacement
"""

import os
import json
import shutil
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from copy import deepcopy
import re

class DocumentGenerator:
    """Generate final documents with HYBRID replacement logic"""
    
    def __init__(self):
        """Initialize the document generator"""
        # Set working directory to script's parent (BID_PROCESSOR)
        self.base_dir = Path(__file__).parent.parent
        os.chdir(self.base_dir)
        
        # Read current batch ID
        self.batch_id = self.read_batch_id()
        if not self.batch_id:
            raise ValueError("❌ No current batch ID found!")
        
        # Set up paths
        self.batch_dir = self.base_dir / self.batch_id
        self.extracted_dir = self.batch_dir / "extracted_data"
        self.docx_dir = self.batch_dir / "docx"
        self.templates_dir = self.base_dir / "templates"
        
        # Ensure directories exist
        self.docx_dir.mkdir(exist_ok=True)
        
        print(f"📄 DocumentGenerator initialized for batch: {self.batch_id}")

    def read_batch_id(self):
        """Read current batch ID from current_batch.txt"""
        try:
            batch_file = self.base_dir / "current_batch.txt"
            with open(batch_file, "r") as f:
                batch_id = f.read().strip()
            return batch_id
        except FileNotFoundError:
            print("❌ current_batch.txt not found!")
            return None

    def load_master_data(self):
        """Load master data to determine replacement strategy"""
        master_file = self.extracted_dir / "master_data.json"
        
        if not master_file.exists():
            raise FileNotFoundError(f"❌ Master data not found: {master_file}")
        
        with open(master_file, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        return master_data

    def copy_template_to_working_file(self, template_name, output_name):
        """Copy template to working file for processing"""
        template_file = self.templates_dir / template_name
        output_file = self.docx_dir / output_name
        
        if not template_file.exists():
            raise FileNotFoundError(f"❌ Template not found: {template_file}")
        
        shutil.copy2(template_file, output_file)
        print(f"✅ Copied template: {template_name} → {output_name}")
        return output_file

    def replace_simple_text_placeholder(self, doc, placeholder_key, content):
        """NEW: Run-level replacement for simple text to preserve surrounding text"""
        placeholder_tag = f"{{{{{placeholder_key}}}}}"
        print(f"📝 Run-level replacement for {placeholder_tag}")
        
        replaced = False
        
        for paragraph in doc.paragraphs:
            # Check if placeholder exists in this paragraph
            full_text = paragraph.text
            if placeholder_tag not in full_text:
                continue
            
            print(f"📍 Found {placeholder_tag} in paragraph: '{full_text[:100]}...'")
            
            # Use YOUR PROVEN cross-run replacement method
            i = 0
            while i < len(paragraph.runs):
                # Try to match across runs
                run_text = ""
                j = i
                while j < len(paragraph.runs) and len(run_text) < 200:
                    run_text += paragraph.runs[j].text
                    j += 1

                    if placeholder_tag in run_text:
                        # Split into 3 parts: before, replacement, after
                        before, after = run_text.split(placeholder_tag, 1)

                        # Clear affected runs
                        for k in range(i, j):
                            paragraph.runs[k].text = ""

                        # Write back: before + replacement + after
                        if before:
                            paragraph.runs[i].text = before
                        
                        # Add replacement text with proper formatting
                        if i + 1 < len(paragraph.runs):
                            paragraph.runs[i + 1].text = content
                            # Ensure proper formatting
                            paragraph.runs[i + 1].font.name = "Times New Roman"
                            paragraph.runs[i + 1].font.size = Pt(14)
                        else:
                            # Create new run if needed
                            new_run = paragraph.add_run(content)
                            new_run.font.name = "Times New Roman"
                            new_run.font.size = Pt(14)
                        
                        if after and i + 2 < len(paragraph.runs):
                            paragraph.runs[i + 2].text = after

                        print(f"✅ Replaced {placeholder_tag} with: '{content}'")
                        replaced = True
                        i = j  # move past replaced section
                        break
                else:
                    continue  # inner loop didn't break
                break  # outer loop: matched a placeholder, break

            i += 1
        
        return replaced

    def replace_structured_placeholder(self, doc, placeholder_key):
        """YOUR PROVEN replacement method for structured content AND tables"""
        placeholder_tag = f"{{{{{placeholder_key}}}}}"
        source_path = self.docx_dir / f"{placeholder_key}_formatted.docx"
        
        if not source_path.exists():
            print(f"❌ Missing source doc: {source_path}")
            return False

        print(f"🔄 Using YOUR PROVEN method for {placeholder_tag}")
        
        source_doc = Document(source_path)
        
        # Handle both paragraphs AND tables from source document
        source_elements = []
        for element in source_doc.element.body:
            if element.tag.endswith('}p'):  # Paragraph
                source_elements.append(('paragraph', element))
            elif element.tag.endswith('}tbl'):  # Table
                source_elements.append(('table', element))

        for i, paragraph in enumerate(doc.paragraphs):
            if placeholder_tag in paragraph.text:
                print(f"📍 Found {placeholder_tag} in paragraph {i}")
                
                p_element = paragraph._element
                parent = p_element.getparent()
                index = parent.index(p_element)
                parent.remove(p_element)

                # Insert all elements (paragraphs AND tables) from source
                for element_type, src_element in reversed(source_elements):
                    new_element = deepcopy(src_element)
                    parent.insert(index, new_element)
                    
                    # Apply formatting for paragraphs
                    if element_type == 'paragraph':
                        try:
                            # Find the corresponding paragraph in the document
                            inserted_p = None
                            for p in doc.paragraphs:
                                if p._element == new_element:
                                    inserted_p = p
                                    break
                            
                            if inserted_p:
                                # YOUR PROVEN FONT PRESERVATION for paragraphs
                                for run in inserted_p.runs:
                                    run.font.size = Pt(14)
                                    run.font.name = "Times New Roman"
                        except:
                            pass  # Skip formatting errors for complex elements
                
                print(f"✅ Applied YOUR PROVEN replacement method with table support")
                return True
        
        return False

    def replace_placeholder_hybrid(self, doc, placeholder_key, master_data):
        """HYBRID replacement: Choose method based on content type"""
        placeholders = master_data.get("placeholders", {})
        
        if placeholder_key not in placeholders:
            print(f"❌ Placeholder {placeholder_key} not found in master data")
            return False
        
        placeholder_data = placeholders[placeholder_key]
        content_type = placeholder_data.get("type", "unknown")
        
        print(f"🎯 Processing {placeholder_key} as type: {content_type}")
        
        if content_type == "simple_text":
            # Use run-level replacement for simple text
            content = placeholder_data.get("content", "")
            return self.replace_simple_text_placeholder(doc, placeholder_key, content)
            
        elif content_type in ["structured_content", "table"]:
            # Use YOUR PROVEN paragraph replacement for complex content
            return self.replace_structured_placeholder(doc, placeholder_key)
            
        else:
            print(f"❌ Unknown content type: {content_type}")
            return False

    def generate_document(self, template_name, output_name, placeholders_to_replace):
        """Generate document with HYBRID replacement logic"""
        print(f"\n📄 GENERATING: {output_name}")
        print("=" * 60)
        
        # Load master data to determine replacement strategies
        master_data = self.load_master_data()
        
        # Copy template to working file
        working_file = self.copy_template_to_working_file(template_name, output_name)
        
        # Load the document
        doc = Document(working_file)
        
        # Replace each placeholder using HYBRID logic
        replaced_count = 0
        for placeholder_key in placeholders_to_replace:
            success = self.replace_placeholder_hybrid(doc, placeholder_key, master_data)
            if success:
                replaced_count += 1
        
        # Save the final document
        doc.save(working_file)
        
        print(f"✅ Generated {output_name}")
        print(f"🔄 Replaced {replaced_count}/{len(placeholders_to_replace)} placeholders")
        
        return working_file, replaced_count

    def load_formatting_summary(self):
        """Load formatting summary to know what content is available"""
        summary_file = self.docx_dir / "formatting_summary.json"
        
        if not summary_file.exists():
            raise FileNotFoundError(f"❌ Formatting summary not found: {summary_file}")
        
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        
        return summary

    def generate_all_documents(self):
        """Generate all documents with hybrid replacement"""
        print("\n📄 GENERATING: All Documents with Hybrid Logic")
        print("=" * 60)
        
        # Load formatting summary
        try:
            summary = self.load_formatting_summary()
        except FileNotFoundError as e:
            print(e)
            return False
        
        available_placeholders = summary.get("formatted_placeholders", [])
        
        if not available_placeholders:
            print("❌ No formatted content available")
            return False
        
        print(f"📊 Available placeholders: {available_placeholders}")
        
        # Document generation rules
        documents_to_generate = [
            {
                "template": "02_MUC_DO_HIEU_BIET_template.docx",
                "output": "02_MUC_DO_HIEU_BIET_output.docx",
                "placeholders": available_placeholders
            }
        ]
        
        generated_documents = []
        
        # Generate each document
        for doc_config in documents_to_generate:
            template_name = doc_config["template"]
            output_name = doc_config["output"]
            placeholders = doc_config["placeholders"]
            
            # Filter to only use available placeholders
            available_placeholders_for_doc = [p for p in placeholders if p in available_placeholders]
            
            if not available_placeholders_for_doc:
                print(f"⚠️ Skipping {output_name} - no available placeholders")
                continue
            
            try:
                output_file, replaced_count = self.generate_document(
                    template_name, 
                    output_name, 
                    available_placeholders_for_doc
                )
                
                generated_documents.append({
                    "file": str(output_file),
                    "template": template_name,
                    "placeholders_replaced": replaced_count,
                    "total_placeholders": len(available_placeholders_for_doc)
                })
                
            except Exception as e:
                print(f"❌ Failed to generate {output_name}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        # Save generation summary
        generation_summary = {
            "batch_id": self.batch_id,
            "generated_documents": generated_documents,
            "total_documents": len(generated_documents),
            "available_placeholders": available_placeholders
        }
        
        summary_file = self.docx_dir / "generation_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(generation_summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ SUCCESS: Generated {len(generated_documents)} documents!")
        for doc in generated_documents:
            print(f"📄 {Path(doc['file']).name}: {doc['placeholders_replaced']}/{doc['total_placeholders']} placeholders")
        
        return len(generated_documents) > 0

def main():
    print("📄 Document Generator - FIXED with Hybrid Replacement Logic")
    print("=" * 70)
    
    try:
        # Initialize generator
        generator = DocumentGenerator()
        print("✅ Generator initialized successfully")
        
        # Generate all documents
        success = generator.generate_all_documents()
        
        if success:
            print("\n🎉 Document generation completed successfully!")
        else:
            print("\n❌ Document generation failed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()