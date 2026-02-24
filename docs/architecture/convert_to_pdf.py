#!/usr/bin/env python3
"""
Convert Markdown architecture documents to PDF
"""

import os
import sys
from pathlib import Path

try:
    from markdown_pdf import MarkdownPdf, Section
except ImportError:
    print("Installing markdown-pdf...")
    os.system("pip install markdown-pdf")
    from markdown_pdf import MarkdownPdf, Section

def convert_md_to_pdf(md_file, pdf_file):
    """Convert a markdown file to PDF"""
    try:
        print(f"Converting {md_file} to {pdf_file}...")
        
        # Read markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create PDF
        pdf = MarkdownPdf()
        pdf.add_section(Section(content))
        pdf.save(pdf_file)
        
        print(f"✓ Successfully created {pdf_file}")
        return True
    except Exception as e:
        print(f"✗ Error converting {md_file}: {e}")
        return False

def main():
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    
    # List of markdown files to convert
    md_files = [
        "01_System_Architecture_Overview.md",
        "02_Multi_Agent_System_Architecture.md",
        "03_Machine_Learning_Architecture.md",
        "04_Medical_Report_Upload_Architecture.md"
    ]
    
    success_count = 0
    total_count = len(md_files)
    
    print("=" * 60)
    print("SymptomSense Architecture Documentation")
    print("Markdown to PDF Converter")
    print("=" * 60)
    print()
    
    for md_file in md_files:
        md_path = script_dir / md_file
        pdf_file = md_file.replace('.md', '.pdf')
        pdf_path = script_dir / pdf_file
        
        if not md_path.exists():
            print(f"✗ File not found: {md_path}")
            continue
        
        if convert_md_to_pdf(str(md_path), str(pdf_path)):
            success_count += 1
    
    print()
    print("=" * 60)
    print(f"Conversion Complete: {success_count}/{total_count} files converted")
    print("=" * 60)
    
    if success_count == total_count:
        print("\n✓ All architecture documents successfully converted to PDF!")
        print(f"\nPDF files location: {script_dir}")
    else:
        print(f"\n⚠ {total_count - success_count} file(s) failed to convert")
        sys.exit(1)

if __name__ == "__main__":
    main()
