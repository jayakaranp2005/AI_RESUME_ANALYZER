"""
PDF parsing module for extracting text from resume PDFs.
Uses pdfplumber to extract text from all pages of each PDF file.
"""

import pdfplumber
import io

def extract_text_from_pdfs(uploaded_files):
    """
    Extract text from multiple PDF files.
    
    Args:
        uploaded_files: List of UploadedFile objects from Streamlit st.file_uploader()
        
    Returns:
        dict: Mapping of filename -> raw extracted text
              Example: {"resume1.pdf": "John Doe...", "resume2.pdf": "Jane Smith..."}
              
    Raises:
        Exception: If PDF cannot be read or has no extractable text
    """
    
    if not uploaded_files:
        return {}
    
    resume_texts = {}
    
    for uploaded_file in uploaded_files:
        try:
            pdf_bytes = uploaded_file.read()
            extracted_text = ""
            
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                if len(pdf.pages) == 0:
                    raise ValueError(f"PDF '{uploaded_file.name}' has no pages")
                
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += page_text + "\n"
            
            if not extracted_text.strip():
                raise ValueError(
                    f"No extractable text found in '{uploaded_file.name}'. "
                    "This may be an image-based PDF."
                )
            
            resume_texts[uploaded_file.name] = extracted_text
            
        except Exception as e:
            print(f"Error processing '{uploaded_file.name}': {str(e)}")
            raise Exception(
                f"Failed to extract text from '{uploaded_file.name}': {str(e)}"
            )
    
    return resume_texts

#TESTING PURPOSE Please remove after testing

if __name__ == "__main__":
    import os

    # Simulate what streamlit uploaded_file looks like
    class FakeUploadedFile:
        def __init__(self, full_path):
            # os.path.basename automatically extracts just the filename (e.g., "resume.pdf")
            self.name = os.path.basename(full_path)
            self._path = full_path
        
        def read(self):
            with open(self._path, "rb") as f:
                return f.read()

    # 1. Path to your local data folder containing the 20+ resumes
    data_folder = "data" 
    
    print(f"Scanning directory: {os.path.abspath(data_folder)}\n")
    
    if not os.path.exists(data_folder):
        print(f"❌ Error: The folder '{data_folder}' does not exist.")
    else:
        # 2. Gather all PDF files found inside the folder
        local_pdf_paths = [
            os.path.join(data_folder, file) 
            for file in os.listdir(data_folder) 
            if file.lower().endswith('.pdf')
        ]
        
        print(f"Found {len(local_pdf_paths)} PDF file(s) for bulk processing.")
        
        # 3. Instantiate your FakeUploadedFile object for each path found
        fake_files = [FakeUploadedFile(path) for path in local_pdf_paths]
        
        # 4. Trigger your extractor function with the batch list
        if fake_files:
            try:
                results = extract_text_from_pdfs(fake_files)
                
                # 5. Loop through the resulting dictionary to print sequentially
                print("\n--- [STARTING BULK TERMINAL STREAM] ---")
                for index, (filename, text) in enumerate(results.items(), start=1):
                    print(f"\n{'-'*30} FILE {index} OF {len(results)} {'-'*30}")
                    print(f"📄 Name      : {filename}")
                    print(f"📊 Length    : {len(text)} characters")
                    print(f"{'-'*75}")
                    
                    # Print first 500 characters cleanly stripped of extra trailing newlines
                    print(text[:2000].strip())
                    print(f"{'='*75}\n")
                    
                print("--- [BULK TESTING COMPLETED SUCCESSFULLY] ---")
                
            except Exception as e:
                print(f"❌ Bulk processing failed: {e}")
        else:
            print("⚠️ No PDF files discovered inside the data directory to execute test.")