import os
import glob
import re # 匯入 re 模組
from pathlib import Path

def combine_summaries(input_dir: str = "../output", output_dir: str = "../final_output", output_filename: str = "combined_summaries.txt"):
    """
    合併指定輸入目錄中的所有 .txt 檔案，將它們的內容格式化為 Markdown，
    並根據集數數字排序後，將結果寫入指定輸出目錄中的單一 .txt 檔案。

    Args:
        input_dir: 包含摘要 .txt 檔案的輸入目錄相對路徑。
        output_dir: 存放合併後檔案的輸出目錄相對路徑。
        output_filename: 合併後的輸出檔名。
    """
    script_dir = Path(__file__).parent
    input_path = script_dir / input_dir
    output_path = script_dir / output_dir
    output_file_path = output_path / output_filename

    # 確保輸入目錄存在
    if not input_path.is_dir():
        print(f"錯誤：輸入目錄 '{input_path}' 不存在或不是一個目錄。")
        return

    # 獲取所有 .txt 檔案的路徑
    all_files = list(input_path.glob("*.txt"))

    # 提取集數並準備排序
    files_to_sort = []
    # 正規表示式匹配 S3EP 後面的數字
    episode_pattern = re.compile(r"S3EP(\d+)_.*\.txt$", re.IGNORECASE)

    for file_path in all_files:
        match = episode_pattern.search(file_path.name)
        if match:
            try:
                episode_number = int(match.group(1))
                files_to_sort.append((episode_number, file_path))
            except ValueError:
                print(f"警告：無法從檔案名 '{file_path.name}' 中解析集數，將忽略此檔案。")
        else:
            print(f"警告：檔案名 '{file_path.name}' 不符合 'S3EPXXX_摘要.txt' 格式，將忽略此檔案。")

    # 根據集數進行數字排序
    sorted_files = sorted(files_to_sort, key=lambda x: x[0])

    if not sorted_files:
        print(f"在 '{input_path}' 中找不到符合格式的 .txt 檔案進行合併。")
        return

    # 創建輸出目錄（如果不存在）
    output_path.mkdir(parents=True, exist_ok=True)

    combined_content = []

    # 按排序後的順序讀取檔案並合併
    for episode_number, file_path in sorted_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 使用檔案名（不含副檔名）作為 Markdown 的二級標題
                file_stem = file_path.stem
                combined_content.append(f"## {file_stem}\n")
                combined_content.append(content)
                combined_content.append("\n---\n")
        except Exception as e:
            print(f"讀取檔案 '{file_path}' 時發生錯誤：{e}")

    # 將合併後的內容寫入輸出檔案
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(combined_content))
        print(f"成功將 {len(sorted_files)} 個摘要（按集數排序）合併到 '{output_file_path}'")
    except Exception as e:
        print(f"寫入檔案 '{output_file_path}' 時發生錯誤：{e}")

if __name__ == "__main__":
    combine_summaries() 