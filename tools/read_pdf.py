from langchain_core.tools import tool
import io 
import PyPDF2
import requests

@tool
def read_pdf(url: str) -> str:
    """Read and extract text from a PDF located at the given URL.
    Args:
        url (str): The URL of the PDF file.
    Returns:
        str: The extracted text from the PDF.
    """
    #TODO 1: Access PDF from URL
    try:
        response = requests.get(url)
        #TODO 2: Convert to Bytes
        pdf_bytes = io.BytesIO(response.content)
        # print(pdf_bytes)
        #TODO 3: Retrieve text from pdf
        pdf_reader = PyPDF2.PdfReader(pdf_bytes)
        num_pages=len(pdf_reader.pages)
        #Extract text from all pages
        text=""
        for i, page in enumerate(pdf_reader.pages, 1):
            print(f"Extracting text from page {i} / {num_pages}")
            text += page.extract_text()+"\n"
        print(f"Successfully extracted {len(text)} characters from PDF") 
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF from {url}: {e}")
        raise ConnectionError(f"Error reading PDF from {url}: {e}")
