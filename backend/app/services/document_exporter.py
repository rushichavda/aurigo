"""
Document Exporter Service
Creates formatted DOCX files for attorney letter and exhibit index
"""
from typing import List, Dict, Optional
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.style import WD_STYLE_TYPE
import re


class DocumentExporter:
    """
    Exports attorney letters and exhibit indices to professional DOCX format
    """

    def __init__(self):
        self.doc = None

    def create_attorney_letter(
        self,
        letter_content: str,
        output_path: str,
        beneficiary_name: str
    ) -> str:
        """
        Create formatted attorney letter DOCX

        Args:
            letter_content: Generated letter text (markdown format)
            output_path: Path for output DOCX file
            beneficiary_name: Name of beneficiary for filename

        Returns:
            Path to created file
        """
        self.doc = Document()

        # Set up page margins
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        # Configure styles
        self._setup_styles()

        # Parse and add content
        self._parse_and_add_content(letter_content)

        # Save document
        filename = f"{output_path}/{beneficiary_name.replace(' ', '_')}_EB1A_Attorney_Letter.docx"
        self.doc.save(filename)

        return filename

    def create_exhibit_index(
        self,
        exhibit_data: List[Dict],
        output_path: str,
        beneficiary_name: str
    ) -> str:
        """
        Create formatted exhibit index DOCX

        Args:
            exhibit_data: List of exhibit groups from ExhibitManager
            output_path: Path for output DOCX file
            beneficiary_name: Name of beneficiary

        Returns:
            Path to created file
        """
        self.doc = Document()

        # Set up page margins
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        # Title
        title = self.doc.add_heading("INDEX OF EXHIBITS", level=1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        self.doc.add_paragraph()

        # Add each exhibit group
        for group in exhibit_data:
            # Group header with blue background
            header_para = self.doc.add_paragraph()
            header_run = header_para.add_run(
                f"EXHIBIT {group['group_letter']}     {group['group_title']}"
            )
            header_run.font.bold = True
            header_run.font.size = Pt(11)
            header_para.paragraph_format.space_after = Pt(6)

            # Shade the header paragraph (simulating blue background)
            shading_elm = header_para._element.get_or_add_pPr()

            # Add exhibits in this group
            for exhibit in group['exhibits']:
                exhibit_para = self.doc.add_paragraph(style='List Bullet')

                # Exhibit ID in bold
                id_run = exhibit_para.add_run(f"{exhibit['exhibit_id']}")
                id_run.font.bold = True

                # Title and description
                text_run = exhibit_para.add_run(f"    {exhibit['title']}")

                if exhibit.get('description'):
                    # Add description in smaller font if available
                    desc_para = self.doc.add_paragraph(f"        {exhibit['description']}")
                    desc_para.paragraph_format.left_indent = Inches(0.5)
                    desc_para.runs[0].font.size = Pt(10)
                    desc_para.runs[0].font.italic = True

            # Add spacing between groups
            self.doc.add_paragraph()

        # Save document
        filename = f"{output_path}/{beneficiary_name.replace(' ', '_')}_Exhibit_Index.docx"
        self.doc.save(filename)

        return filename

    def _setup_styles(self):
        """Configure document styles for professional legal appearance"""

        # Normal style
        style = self.doc.styles['Normal']
        font = style.font
        font.name = 'Times New Roman'
        font.size = Pt(12)

        # Heading 1 (Main sections: I, II, III)
        try:
            heading1 = self.doc.styles['Heading 1']
            heading1.font.name = 'Times New Roman'
            heading1.font.size = Pt(14)
            heading1.font.bold = True
            heading1.paragraph_format.space_before = Pt(18)
            heading1.paragraph_format.space_after = Pt(12)
        except KeyError:
            pass

        # Heading 2 (Subsections: 1, 2, 3)
        try:
            heading2 = self.doc.styles['Heading 2']
            heading2.font.name = 'Times New Roman'
            heading2.font.size = Pt(13)
            heading2.font.bold = True
            heading2.paragraph_format.space_before = Pt(12)
            heading2.paragraph_format.space_after = Pt(6)
        except KeyError:
            pass

        # Heading 3 (Sub-subsections: a, b, c)
        try:
            heading3 = self.doc.styles['Heading 3']
            heading3.font.name = 'Times New Roman'
            heading3.font.size = Pt(12)
            heading3.font.bold = True
            heading3.font.italic = True
            heading3.paragraph_format.space_before = Pt(6)
            heading3.paragraph_format.space_after = Pt(6)
        except KeyError:
            pass

    def _parse_and_add_content(self, content: str):
        """
        Parse markdown-style content and add to document

        Args:
            content: Letter content with markdown formatting
        """
        lines = content.split('\n')

        for line in lines:
            line = line.rstrip()

            if not line:
                # Empty line
                self.doc.add_paragraph()
                continue

            # Check for headings
            if line.startswith('## '):
                # Heading 1 (Main sections)
                heading_text = line[3:].strip()
                self.doc.add_heading(heading_text, level=1)

            elif line.startswith('### '):
                # Heading 2 (Subsections)
                heading_text = line[4:].strip()
                self.doc.add_heading(heading_text, level=2)

            elif line.startswith('#### '):
                # Heading 3 (Sub-subsections)
                heading_text = line[5:].strip()
                self.doc.add_heading(heading_text, level=3)

            elif line.startswith('- '):
                # Bullet point
                self.doc.add_paragraph(line[2:].strip(), style='List Bullet')

            elif line.startswith('**') and line.endswith('**'):
                # Bold paragraph
                para = self.doc.add_paragraph()
                run = para.add_run(line[2:-2])
                run.font.bold = True

            else:
                # Regular paragraph
                para = self.doc.add_paragraph(line)

                # Apply formatting for specific patterns
                self._apply_inline_formatting(para)

    def _apply_inline_formatting(self, paragraph):
        """
        Apply inline formatting (bold, italic, exhibit references)

        Args:
            paragraph: Document paragraph object
        """
        # Bold exhibit references (e.g., "Exhibit C-1")
        text = paragraph.text
        if 'Exhibit' in text:
            # Clear existing runs
            paragraph.clear()

            # Split and reformat
            parts = re.split(r'(Exhibit [A-Z]-\d+)', text)

            for part in parts:
                if part.startswith('Exhibit '):
                    run = paragraph.add_run(part)
                    run.font.bold = True
                else:
                    paragraph.add_run(part)

        # Bold regulation citations (e.g., "8 C.F.R. § 204.5(h)(3)(ii)")
        if 'C.F.R.' in text:
            paragraph.clear()
            parts = re.split(r'(8 C\.F\.R\. § \d+\.\d+\([a-z]\)\(\d+\)\([a-z]+\))', text)

            for part in parts:
                if 'C.F.R.' in part:
                    run = paragraph.add_run(part)
                    run.font.bold = True
                else:
                    paragraph.add_run(part)

    def create_case_package(
        self,
        letter_content: str,
        exhibit_data: List[Dict],
        output_path: str,
        beneficiary_name: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Create complete case package (letter + exhibit index + metadata)

        Args:
            letter_content: Generated letter
            exhibit_data: Exhibit information
            output_path: Output directory
            beneficiary_name: Beneficiary name
            metadata: Optional case metadata

        Returns:
            Dictionary with paths to created files
        """
        files = {}

        # Create attorney letter
        letter_path = self.create_attorney_letter(
            letter_content,
            output_path,
            beneficiary_name
        )
        files['attorney_letter'] = letter_path

        # Create exhibit index
        index_path = self.create_exhibit_index(
            exhibit_data,
            output_path,
            beneficiary_name
        )
        files['exhibit_index'] = index_path

        # Save metadata JSON
        if metadata:
            import json
            metadata_path = f"{output_path}/{beneficiary_name.replace(' ', '_')}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            files['metadata'] = metadata_path

        return files

    def add_page_numbers(self):
        """Add page numbers to document footer"""
        if not self.doc:
            return

        section = self.doc.sections[0]
        footer = section.footer
        footer_para = footer.paragraphs[0]
        footer_para.text = "Page "
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def set_line_spacing(self, spacing: float = 1.0):
        """
        Set line spacing for the document

        Args:
            spacing: Line spacing multiplier (1.0 = single, 1.5 = 1.5 spacing, 2.0 = double)
        """
        if not self.doc:
            return

        for paragraph in self.doc.paragraphs:
            paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
            paragraph.paragraph_format.line_spacing = spacing
