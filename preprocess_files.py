import os
from unstructured.partition.pdf import partition_pdf
from bs4 import BeautifulSoup
from unstructured.partition.docx import partition_docx

# Specify the directory to save the text files
output_dir = "output_text_files"
os.makedirs(output_dir, exist_ok=True)

def save_to_file(file_name, elements):
    """Save the extracted content to a text file."""
    with open(os.path.join(output_dir, file_name), 'w') as f:
        for element in elements:
            f.write(str(element) + "\n\n")

def process_pdf_files(pdf_files):
    """Process multiple PDF files and save their content."""
    for pdf_file in pdf_files:
        print(f"Processing {pdf_file}...")
        elements = partition_pdf(filename=pdf_file)
        output_file_name = os.path.basename(pdf_file).replace('.pdf', '.txt')
        save_to_file(output_file_name, elements)

def process_html_file(html_file):
    """Process an HTML file and save its content."""
    # print(f"Processing {html_file}...")
    # elements = partition_html(filename=html_file)
    # output_file_name = os.path.basename(html_file).replace('.html', '.txt')
    # save_to_file(output_file_name, elements)
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    return soup.get_text()

def process_docx_files(docx_files):
    """Process multiple Word (.docx) files and save their content."""
    for docx_file in docx_files:
        print(f"Processing {docx_file}...")
        elements = partition_docx(filename=docx_file)
        output_file_name = os.path.basename(docx_file).replace('.docx', '.txt')
        save_to_file(output_file_name, elements)

if __name__ == "__main__":
    # List of PDF files to process
    pdf_files = ['/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/408880.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/370433.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/370432.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/380716.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/410799.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/370430.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/370431.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/389719.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/387650.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/389720.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/387651.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/406274.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/DS_Data_guidance_on_quality_requirements_for_medicinal_cannabis_products_conforming_with _TGO_93_V1_20240611.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/412110.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/442335.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/442334.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/333147.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/DS_Data_Introduction_to_Medicinal Cannabis_2nd_Edition_V1_20240611.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/348491.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/373214.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/403958.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/442333.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/373217.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/381258.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/417505.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/380811.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/408590.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/376189.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/417502.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/417501.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/333148.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/386353.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/381990.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/451246.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/420871.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/386355.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/386354.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/420870.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/420872.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/386356.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/399510.pdf', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/326240.pdf']
    
    # HTML file to process
    html_file = "/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/DS_Data_Australia_Legal_Cannabis_Market_Size_&_Share_Report_2030_V1_20240611.html"

    docx_files = ['/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/DS_Data_TGO93_Compilation_No.3_Dec_2022_V1_20240611.docx', '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/DS_Data_advertising_guidance_businesses_medicinal_cannabis_products_V1_20240611.docx']
    
    # Process the files
    process_pdf_files(pdf_files)
    process_html_file(html_file)
    process_docx_files(docx_files)

    print(f"All files have been processed and saved in the '{output_dir}' folder.")
