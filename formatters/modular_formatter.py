#!/usr/bin/env python3
"""
Modular Format Dispatcher
Calls specialized formatters based on content type for maximum reusability
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime

# Import our modular formatters
sys.path.append(str(Path(__file__).parent))
from format_simple_text import SimpleTextFormatter
from format_table import TableFormatter
from format_structured import StructuredContentFormatter

class ModularFormatter:
    """Dispatcher that routes to specialized formatters for scalability"""
    
    def __init__(self):
        """Initialize the modular formatter dispatcher"""
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
        
        # Ensure directories exist
        self.docx_dir.mkdir(exist_ok=True)
        
        print(f"🎨 ModularFormatter initialized for batch: {self.batch_id}")
        print(f"📁 Data source: {self.extracted_dir}")
        print(f"📁 Output directory: {self.docx_dir}")

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
        """Load master_data.json"""
        master_file = self.extracted_dir / "master_data.json"
        
        if not master_file.exists():
            raise FileNotFoundError(f"❌ Master data not found: {master_file}")
        
        with open(master_file, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        print(f"📊 Loaded master data with {len(master_data.get('placeholders', {}))} placeholders")
        return master_data

    def dispatch_formatter(self, placeholder_key, placeholder_data):
        """Route to appropriate specialized formatter based on content type"""
        content_type = placeholder_data.get("type", "simple_text")
        content = placeholder_data.get("content")
        
        print(f"🎨 Dispatching {placeholder_key} to {content_type} formatter")
        
        try:
            if content_type == "simple_text":
                formatter = SimpleTextFormatter(self.batch_id)
                return formatter.format_simple_text(placeholder_key, content)
                
            elif content_type == "table":
                formatter = TableFormatter(self.batch_id)
                return formatter.format_table(placeholder_key, content)
                
            elif content_type == "structured_content":
                formatter = StructuredContentFormatter(self.batch_id)
                return formatter.format_structured_content(placeholder_key, content)
                
            else:
                print(f"⚠️ Unknown content type: {content_type}, defaulting to simple text")
                formatter = SimpleTextFormatter(self.batch_id)
                return formatter.format_simple_text(placeholder_key, str(content))
                
        except Exception as e:
            print(f"❌ Error in {content_type} formatter: {str(e)}")
            return None

    def format_all_extracted_content(self):
        """Format all extracted content using modular approach"""
        print("\n🎨 MODULAR FORMATTING: All extracted content")
        print("=" * 60)
        
        # Load master data
        try:
            master_data = self.load_master_data()
        except FileNotFoundError as e:
            print(e)
            return False
        
        placeholders = master_data.get("placeholders", {})
        extraction_log = master_data.get("extraction_log", {})
        
        if not placeholders:
            print("❌ No placeholders found in master data")
            return False
        
        formatted_files = {}
        
        # Format each placeholder using specialized formatters
        for placeholder_key, placeholder_data in placeholders.items():
            # Check if extraction was successful
            log_entry = extraction_log.get(placeholder_key, {})
            if log_entry.get("status") != "success":
                print(f"⚠️ Skipping {placeholder_key} - extraction failed: {log_entry.get('error', 'Unknown error')}")
                continue
            
            try:
                formatted_file = self.dispatch_formatter(placeholder_key, placeholder_data)
                if formatted_file:
                    formatted_files[placeholder_key] = formatted_file
                    print(f"✅ Formatted {placeholder_key} using modular approach")
                else:
                    print(f"❌ Failed to format {placeholder_key}")
                
            except Exception as e:
                print(f"❌ Failed to format {placeholder_key}: {str(e)}")
                continue
        
        # Save formatting summary
        summary = {
            "batch_id": self.batch_id,
            "formatted_placeholders": list(formatted_files.keys()),
            "formatted_files": {k: str(v) for k, v in formatted_files.items()},
            "total_formatted": len(formatted_files),
            "formatter_type": "modular",
            "timestamp": datetime.now().isoformat()
        }
        
        summary_file = self.docx_dir / "formatting_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ SUCCESS: Modular formatting completed!")
        print(f"📄 Formatted placeholders: {list(formatted_files.keys())}")
        print(f"📊 Used specialized formatters: {len(formatted_files)} placeholders")
        print(f"📋 Summary saved: {summary_file}")
        
        return len(formatted_files) > 0

def main():
    print("🎨 Modular Formatter - Specialized Reusable Components")
    print("=" * 70)
    
    try:
        # Initialize modular formatter
        formatter = ModularFormatter()
        print("✅ Modular formatter initialized successfully")
        
        # Format all content using modular approach
        success = formatter.format_all_extracted_content()
        
        if success:
            print("\n🎉 Modular formatting completed successfully!")
            print("🎯 Ready for Phase 3: Document Generation")
        else:
            print("\n❌ Modular formatting failed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()