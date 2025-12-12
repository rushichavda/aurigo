"""
Document Parser Service using Docling for EB-1A Evidence Processing
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
import mimetypes
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions


class DocumentParser:
    """
    Document parser using Docling for high-accuracy extraction
    Supports PDFs, DOCX, images, and other document formats
    """

    def __init__(self):
        """Initialize Docling converter with default settings"""
        # Use default converter settings (docling 2.58+ has simplified API)
        # OCR and table extraction are enabled by default
        try:
            # Try with allowed_formats first (newer API)
            self.converter = DocumentConverter(
                allowed_formats=[
                    InputFormat.PDF,
                    InputFormat.IMAGE,
                    InputFormat.DOCX,
                    InputFormat.PPTX,
                    InputFormat.HTML,
                    InputFormat.MD,
                ]
            )
        except TypeError:
            # Fallback to simplest initialization if allowed_formats not supported
            self.converter = DocumentConverter()

    def parse_document(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a document and extract all content

        Args:
            file_path: Path to the document file

        Returns:
            Dictionary containing:
                - text: Full extracted text
                - tables: List of extracted tables
                - metadata: Document metadata
                - format: Original document format
                - success: Whether parsing succeeded
                - error: Error message if failed
        """
        try:
            path = Path(file_path)

            if not path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "text": "",
                    "tables": [],
                    "metadata": {}
                }

            # Detect file type
            mime_type, _ = mimetypes.guess_type(str(path))
            file_format = self._get_input_format(path.suffix, mime_type)

            # Convert document
            result = self.converter.convert(str(path))

            # Extract content
            doc = result.document

            # Get full text
            text_content = doc.export_to_markdown()

            # Extract tables
            tables = self._extract_tables(doc)

            # Extract metadata
            metadata = {
                "filename": path.name,
                "format": file_format,
                "mime_type": mime_type,
                "size_bytes": path.stat().st_size,
                "num_pages": len(doc.pages) if hasattr(doc, 'pages') else 1,
            }

            return {
                "success": True,
                "text": text_content,
                "tables": tables,
                "metadata": metadata,
                "format": file_format,
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "tables": [],
                "metadata": {"filename": Path(file_path).name}
            }

    def parse_batch(
        self,
        file_paths: List[str],
        include_errors: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Parse multiple documents in batch

        Args:
            file_paths: List of file paths to parse
            include_errors: Whether to include failed parses in results

        Returns:
            List of parsed document results
        """
        results = []

        for file_path in file_paths:
            result = self.parse_document(file_path)

            if include_errors or result["success"]:
                result["file_path"] = file_path
                results.append(result)

        return results

    def extract_from_folder(
        self,
        folder_path: str,
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract content from all documents in a folder

        Args:
            folder_path: Path to the folder
            recursive: Whether to search subfolders
            file_extensions: List of extensions to include (e.g., ['.pdf', '.docx'])

        Returns:
            List of parsed documents with folder structure
        """
        path = Path(folder_path)

        if not path.exists() or not path.is_dir():
            return []

        # Default supported extensions
        if file_extensions is None:
            file_extensions = ['.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png', '.pptx', '.html']

        # Find all matching files
        if recursive:
            files = [
                str(f) for f in path.rglob('*')
                if f.is_file() and f.suffix.lower() in file_extensions
            ]
        else:
            files = [
                str(f) for f in path.glob('*')
                if f.is_file() and f.suffix.lower() in file_extensions
            ]

        # Parse all files
        results = self.parse_batch(files)

        # Add relative path information
        for result in results:
            full_path = Path(result["file_path"])
            result["relative_path"] = str(full_path.relative_to(path))
            result["parent_folder"] = full_path.parent.name

        return results

    def _get_input_format(self, suffix: str, mime_type: Optional[str]) -> str:
        """Determine input format from file extension and MIME type"""
        suffix = suffix.lower()

        if suffix == '.pdf':
            return 'PDF'
        elif suffix in ['.docx', '.doc']:
            return 'DOCX'
        elif suffix in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            return 'IMAGE'
        elif suffix in ['.pptx', '.ppt']:
            return 'PPTX'
        elif suffix in ['.html', '.htm']:
            return 'HTML'
        elif suffix in ['.md', '.markdown']:
            return 'MD'
        else:
            return 'UNKNOWN'

    def _extract_tables(self, doc) -> List[Dict[str, Any]]:
        """Extract tables from Docling document"""
        tables = []

        try:
            # Docling stores tables in the document structure
            if hasattr(doc, 'tables'):
                for idx, table in enumerate(doc.tables):
                    table_data = {
                        "table_id": idx,
                        "markdown": table.export_to_markdown() if hasattr(table, 'export_to_markdown') else str(table),
                        "rows": len(table.rows) if hasattr(table, 'rows') else 0,
                        "cols": len(table.cols) if hasattr(table, 'cols') else 0,
                    }
                    tables.append(table_data)

        except Exception as e:
            # If table extraction fails, return empty list
            pass

        return tables

    def get_document_preview(self, file_path: str, max_chars: int = 500) -> str:
        """
        Get a preview of document content

        Args:
            file_path: Path to document
            max_chars: Maximum characters to return

        Returns:
            Preview text
        """
        result = self.parse_document(file_path)

        if not result["success"]:
            return f"Error: {result['error']}"

        text = result["text"]
        if len(text) > max_chars:
            return text[:max_chars] + "..."

        return text
