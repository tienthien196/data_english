import os

def list_all_pdf_files(root_dir):
    pdf_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.pdf'):
                pdf_files.append(filename)
    return sorted(pdf_files)  # sắp xếp theo thứ tự bảng chữ cái để dễ đọc

if __name__ == "__main__":
    root_directory = r"E:\DATA\1_test_Src\src\python\web_up_pdf\docs"
    output_file = "list_pdf.txt"
    
    pdf_list = list_all_pdf_files(root_directory)
    
    with open(output_file, "w", encoding="utf-8") as f:
        for name in pdf_list:
            f.write(name + "\n")
    
    print(f"Đã xuất {len(pdf_list)} tên file PDF vào {os.path.abspath(output_file)}")