"""
PDF Parser Module
Extracts and parses requirements from PDF RFP documents
"""

import os
import logging
from typing import Dict, List, Tuple
import pdfplumber
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFParser:
    """Parse PDF RFP documents and extract text content"""

    def __init__(self, max_file_size_mb: int = 50):
        """
        Initialize PDF parser

        Args:
            max_file_size_mb: Maximum allowed file size in MB
        """
        self.max_file_size_mb = max_file_size_mb

    def validate_pdf(self, pdf_path: str) -> Tuple[bool, str]:
        """
        Validate PDF file existence and size

        Args:
            pdf_path: Path to PDF file

        Returns:
            Tuple of (is_valid, message)
        """
        try:
            if not os.path.exists(pdf_path):
                return False, f"File not found: {pdf_path}"

            if not pdf_path.lower().endswith('.pdf'):
                return False, "File must be a PDF document"

            file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                return False, f"File size ({file_size_mb:.2f}MB) exceeds maximum ({self.max_file_size_mb}MB)"

            return True, "PDF is valid"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract all text from PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text content
        """
        try:
            is_valid, message = self.validate_pdf(pdf_path)
            if not is_valid:
                raise ValueError(message)

            text = []
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text.append(f"--- PAGE {page_num} ---\n{page_text}")

            logger.info(f"Successfully extracted text from {pdf_path}")
            return "\n\n".join(text)

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def extract_text_with_structure(self, pdf_path: str) -> Dict:
        """
        Extract text while preserving page structure

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with structured content
        """
        try:
            is_valid, message = self.validate_pdf(pdf_path)
            if not is_valid:
                raise ValueError(message)

            pages_data = []
            with pdfplumber.open(pdf_path) as pdf:
                metadata = pdf.metadata
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_content = {
                        'page_number': page_num,
                        'text': page.extract_text() or '',
                        'tables': page.extract_tables() or [],
                        'height': page.height,
                        'width': page.width,
                    }
                    pages_data.append(page_content)

            result = {
                'filename': Path(pdf_path).name,
                'total_pages': len(pages_data),
                'metadata': metadata,
                'pages': pages_data,
            }

            logger.info(f"Successfully extracted structured content from {pdf_path}")
            return result

        except Exception as e:
            logger.error(f"Error extracting structured content: {str(e)}")
            raise

    def extract_tables(self, pdf_path: str) -> List[List]:
        """
        Extract all tables from PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of extracted tables
        """
        try:
            is_valid, message = self.validate_pdf(pdf_path)
            if not is_valid:
                raise ValueError(message)

            all_tables = []
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            all_tables.append({
                                'page': page_num,
                                'data': table
                            })

            logger.info(f"Extracted {len(all_tables)} tables from {pdf_path}")
            return all_tables

        except Exception as e:
            logger.error(f"Error extracting tables: {str(e)}")
            raise

    def get_pdf_metadata(self, pdf_path: str) -> Dict:
        """
        Extract PDF metadata

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary of PDF metadata
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                return pdf.metadata

        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    parser = PDFParser()
    
    # Example: Extract from sample RFP
    sample_pdf = "./samples/sample_rfp.pdf"
    if os.path.exists(sample_pdf):
        text = parser.extract_text(sample_pdf)
        print("Extracted Text Preview:")
        print(text[:500] + "...")
