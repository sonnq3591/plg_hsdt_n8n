#!/usr/bin/env python3
"""
Simple Text Formatter
Formats simple text content with standard 14pt Times New Roman
"""

import os
import json
from pathlib import Path
from docx import Document
from docx.shared import Pt
from datetime import datetime

class SimpleTextFormatter:
    def __init__(self, batch_id):
        self.batch_id = batch_id
        self.base_dir = Path(__file__).parent.parent
        self.batch_dir = self.base_dir / batch_id
        self.extracted_dir = self.batch_dir / "extracted_data"
        self.docx_dir = self.batch_dir / "docx"
        
        print(f"📝 SimpleTextFormatter initialized for batch: {batch_id}")

    def format_simple_text(self, placeholder_key, content):
        """Format simple text content"""
        print(f"📝 Formatting {placeholder_key} as simple text")
        
        # Create document
        doc = Document()
        style = doc.styles['Normal']
        style.font.name = 'Times New Roman'
        style.font.size = Pt(14)
        
        # Add simple paragraph
        para = doc.add_paragraph(content)
        
        # Minimal formatting - let template control styling
        for run in para.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
        
        # Save
        output_path = self.docx_dir / f"{placeholder_key}_formatted.docx"
        doc.save(output_path)
        print(f"✅ Saved: {output_path}")
        
        return output_path

def main():
    # Test standalone
    if len(sys.argv) > 1:
        batch_id = sys.argv[1]
        formatter = SimpleTextFormatter(batch_id)
        # Test with sample content
        formatter.format_simple_text("test", "Sample text content")

if __name__ == "__main__":
    import sys
    main()