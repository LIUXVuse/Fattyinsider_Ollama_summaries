import os
import re
from pathlib import Path
import math # 匯入 math 模組

def combine_summaries_in_batches(input_dir: str = "../output", output_dir: str = "../final_output", batch_size: int = 25):
    """
    合併指定輸入目錄中的所有 .txt 檔案，按集數數字排序後，
    將它們分成指定大小的批次，並將每個批次的結果寫入到輸出目錄下的單獨檔案中。

    Args:
        input_dir: 包含摘要 .txt 檔案的輸入目錄相對路徑。
        output_dir: 存放合併後批次檔案的輸出目錄相對路徑。
        batch_size: 每個批次檔案包含的最大摘要數量。
    """
    script_dir = Path(__file__).parent
    input_path = script_dir / input_dir
    output_path = script_dir / output_dir

    # 確保輸入目錄存在
    if not input_path.is_dir():
        print(f"錯誤：輸入目錄 '{input_path}' 不存在或不是一個目錄。")
        return

    # 獲取所有 .txt 檔案的路徑
    all_files = list(input_path.glob("*.txt"))

    # 提取集數並準備排序
    files_to_sort = []
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

    total_files = len(sorted_files)
    num_batches = math.ceil(total_files / batch_size)
    created_files_count = 0

    print(f"共找到 {total_files} 個符合格式的摘要檔案，將分成 {num_batches} 個批次處理 (每批最多 {batch_size} 個)。")

    for i in range(num_batches):
        start_index = i * batch_size
        end_index = start_index + batch_size
        batch_files = sorted_files[start_index:end_index]

        if not batch_files:
            continue # 理論上不應發生，但加個保險

        # 獲取批次的起始和結束集數編號
        start_episode = batch_files[0][0]
        end_episode = batch_files[-1][0]
        # 構造輸出檔名
        output_filename = f"S3EP{start_episode}-S3EP{end_episode}_combined_summaries.txt"
        output_file_path = output_path / output_filename

        combined_content = []
        batch_file_count = 0
        for episode_number, file_path in batch_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_stem = file_path.stem
                    combined_content.append(f"## {file_stem}\n")
                    combined_content.append(content)
                    combined_content.append("\n---\n")
                    batch_file_count += 1
            except Exception as e:
                print(f"讀取檔案 '{file_path}' 時發生錯誤：{e}")

        # 將合併後的內容寫入批次輸出檔案
        if combined_content:
            try:
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(combined_content))
                print(f"批次 {i+1}/{num_batches}: 成功將 {batch_file_count} 個摘要合併到 '{output_file_path}'")
                created_files_count += 1
            except Exception as e:
                print(f"寫入檔案 '{output_file_path}' 時發生錯誤：{e}")
        else:
            print(f"批次 {i+1}/{num_batches}: 沒有內容可寫入檔案 '{output_file_path}'")

    print(f"\n處理完成，共成功創建 {created_files_count} 個合併摘要檔案。")

if __name__ == "__main__":
    combine_summaries_in_batches() # 呼叫新的函數 