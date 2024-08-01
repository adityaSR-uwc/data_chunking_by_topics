import os

def get_files_by_type(folder_path):
    pdf_files = []
    html_files = []
    docx_files = []

    # Traverse through all files and subdirectories within the folder
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.pdf'):
                pdf_files.append(os.path.abspath(file_path))
            elif file.endswith('.html') or file.endswith('.htm'):
                html_files.append(os.path.abspath(file_path))
            elif file.endswith('.docx'):
                docx_files.append(os.path.abspath(file_path))

    return {
        'pdf_files': pdf_files,
        'html_files': html_files,
        'docx_files': docx_files
    }

folder_path = '/Users/asr/Desktop/UWC/unstructed-cannabis_data/data'

file_paths_by_type = get_files_by_type(folder_path)

# Print the results
print("PDF Files:")
print(file_paths_by_type['pdf_files'])
print("\nHTML Files:")
print(file_paths_by_type['html_files'])
print("\nDOCX Files:")
print(file_paths_by_type['docx_files'])
