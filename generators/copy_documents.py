#!/usr/bin/env python3
"""
Simple Template Copier
Copy the 5 templates to current batch docx folder for testing
"""

import os
import shutil
from pathlib import Path

def copy_templates():
    """Copy the 5 templates to batch docx folder"""
    
    # Set working directory to script's parent (BID_PROCESSOR)
    base_dir = Path(__file__).parent.parent
    os.chdir(base_dir)
    
    # Read current batch ID
    try:
        batch_file = base_dir / "current_batch.txt"
        with open(batch_file, "r") as f:
            batch_id = f.read().strip()
    except FileNotFoundError:
        print("❌ current_batch.txt not found!")
        return
    
    print(f"📁 Current batch: {batch_id}")
    
    # Set up paths
    batch_dir = base_dir / batch_id
    docx_dir = batch_dir / "docx"
    templates_dir = base_dir / "templates"
    
    # Ensure docx directory exists
    docx_dir.mkdir(exist_ok=True)
    
    # Document configurations like document_to_generate
    documents_to_copy = [
        {
            "template": "01_TINH_HIEU_QUA_CONG_VIEC_template.docx",
            "output": "01_TINH_HIEU_QUA_CONG_VIEC.docx"
        },
        {
            "template": "03_CAC_BUOC_VA_CACH_THUC_THUC_HIEN_template.docx",
            "output": "03_CAC_BUOC_VA_CACH_THUC_THUC_HIEN.docx"
        },
        {
            "template": "07_DE_XUAT_GIAI_PHAP_template.docx",
            "output": "07_DE_XUAT_GIAI_PHAP.docx"
        },
        {
            "template": "09_THUYET_MINH_PHAN_MEM_CHINH_LY_template.docx",
            "output": "09_THUYET_MINH_PHAN_MEM_CHINH_LY.docx"
        },
        {
            "template": "13_TM_BIEN_PHAP_VSMT_PCCC_template.docx",
            "output": "13_TM_BIEN_PHAP_VSMT_PCCC.docx"
        }
    ]
    
    copied_count = 0
    
    for doc_config in documents_to_copy:
        template_file = doc_config["template"]
        output_file = doc_config["output"]
        
        source_path = templates_dir / template_file
        dest_path = docx_dir / output_file
        
        if source_path.exists():
            try:
                shutil.copy2(source_path, dest_path)
                print(f"✅ Copied: {template_file} → {output_file}")
                copied_count += 1
            except Exception as e:
                print(f"❌ Failed to copy {template_file}: {e}")
        else:
            print(f"⚠️ Template not found: {template_file}")
    
    print(f"\n📊 Summary:")
    print(f"   Copied: {copied_count} templates")
    print(f"   To directory: {docx_dir}")
    
    # List what's in the docx directory now
    if docx_dir.exists():
        files = list(docx_dir.glob("*.docx"))
        print(f"   Files in docx folder: {len(files)}")
        for file in sorted(files):
            print(f"     - {file.name}")

def main():
    print("📄 Template Copier - Copy 5 Templates to Batch Folder")
    print("=" * 60)
    
    try:
        copy_templates()
        print("\n🎉 Template copying completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()