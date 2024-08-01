import os
from unstructured.partition.html import partition_html

output_dir = "output_text_files_html"
os.makedirs(output_dir, exist_ok=True)

def save_to_file(file_name, elements):
    """Save the extracted content to a text file."""
    with open(os.path.join(output_dir, file_name), 'w') as f:
        for element in elements:
            f.write(str(element) + "\n\n")

def process_html_file(html_file):
    """Process an HTML file and save its content."""
    print(f"Processing {html_file}...")
    elements = partition_html(filename=html_file)
    output_file_name = os.path.basename(html_file).replace('.html', '.txt')
    save_to_file(output_file_name, elements)


if __name__ == "__main__":
   
    html_file = "/Users/asr/Desktop/UWC/unstructed-cannabis_data/data/DS_Data_Australia_Legal_Cannabis_Market_Size_&_Share_Report_2030_V1_20240611.html"
    
    process_html_file(html_file)

    print(f"All files have been processed and saved in the '{output_dir}' folder.")
