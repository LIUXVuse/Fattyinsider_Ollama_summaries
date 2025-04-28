# -*- coding: utf-8 -*-

import os
import ollama
import re
import logging
from pathlib import Path
from collections import defaultdict

# 設定日誌記錄
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 設定 ---
# 輸入資料夾：指向專案根目錄下的 faty_talk 資料夾
INPUT_DIR = Path("../faty_talk")  # 相對於 src 資料夾
OUTPUT_DIR = Path("../output") # 摘要輸出的資料夾
MODEL_NAME = "gemma3:27b"  # 您偏好的 Ollama 模型
OLLAMA_HOST = "http://localhost:11434" # 本地 Ollama 服務地址

# 確保輸出資料夾存在 (在 main 函數中處理)

def find_files_to_process(directory: Path) -> list:
    """
    查找需要處理的檔案。
    優先找出 talk/ver 配對，若無配對，則找出該 ID 下的第一個檔案作為單一處理對象。
    返回一個列表，包含要處理的項目信息 (id, type, paths)。
    """
    files_by_id = defaultdict(list)
    all_files_pattern = re.compile(r"^(S3EP\d+).*\.txt$", re.IGNORECASE)
    talk_pattern = re.compile(r"^(S3EP\d+?)_talk(?:\..*?)?\.txt$", re.IGNORECASE)
    ver_pattern = re.compile(r"^(S3EP\d+?)_Ver(?:\..*?)?\.txt$", re.IGNORECASE)

    logging.info(f"正在掃描資料夾: {directory.resolve()}")
    actual_input_dir = directory.resolve()

    if not actual_input_dir.is_dir():
        logging.error(f"輸入資料夾不存在或不是一個目錄: {actual_input_dir}")
        return []

    # 收集所有 S3EPXXX 開頭的 txt 檔案
    for item in actual_input_dir.iterdir():
        if item.is_file():
            match = all_files_pattern.match(item.name)
            if match:
                identifier = match.group(1).upper()
                files_by_id[identifier].append(item)
                logging.debug(f"找到檔案: {item.name}，歸類於 ID: {identifier}")
            else:
                logging.debug(f"檔案 {item.name} 不符合 S3EPXXX...txt 命名規則，已忽略。")

    process_list = []
    processed_ids = set()

    # 優先處理配對
    for identifier, file_list in files_by_id.items():
        talk_file = None
        ver_file = None
        # 在該 ID 的檔案列表中尋找 talk 和 ver 檔案
        for file_path in file_list:
            if talk_pattern.match(file_path.name):
                if talk_file is None: # 只取第一個找到的 talk
                    talk_file = file_path
                else:
                    logging.debug(f"ID {identifier} 找到多個 talk 檔案，僅使用第一個: {talk_file.name}")
            elif ver_pattern.match(file_path.name):
                if ver_file is None: # 只取第一個找到的 ver
                    ver_file = file_path
                else:
                    logging.debug(f"ID {identifier} 找到多個 ver 檔案，僅使用第一個: {ver_file.name}")

        if talk_file and ver_file:
            process_list.append({
                'id': identifier,
                'type': 'pair',
                'talk': talk_file,
                'ver': ver_file
            })
            processed_ids.add(identifier)
            logging.info(f"找到配對: {identifier} -> Talk: {talk_file.name}, Ver: {ver_file.name}")

    # 處理沒有成功配對的 ID (取其第一個檔案)
    for identifier, file_list in files_by_id.items():
        if identifier not in processed_ids:
            if file_list:
                # 對檔案列表排序，確保每次執行選擇的檔案一致
                sorted_files = sorted(file_list, key=lambda p: p.name)
                single_file = sorted_files[0]
                process_list.append({
                    'id': identifier,
                    'type': 'single',
                    'path': single_file
                })
                logging.info(f"ID {identifier} 未找到完整 talk/ver 配對，將單獨處理檔案: {single_file.name}")
            else:
                 # 理論上不應發生，因為 files_by_id 是從找到的檔案建立的
                 logging.warning(f"ID {identifier} 在 file_list 中為空，無法處理。")

    # 根據 ID 排序處理列表，確保輸出順序穩定
    process_list.sort(key=lambda x: x['id'])

    logging.info(f"掃描完成，共需處理 {len(process_list)} 個項目 (包含配對與單一檔案)。")
    return process_list

def read_file_content(file_path: Path) -> str:
    """讀取指定檔案的內容"""
    try:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            logging.warning(f"使用 UTF-8 讀取檔案 {file_path} 失敗，嘗試使用 CP950...")
            with open(file_path, 'r', encoding='cp950') as f:
                 return f.read()
    except Exception as e:
        logging.error(f"讀取檔案 {file_path} 時發生錯誤: {e}")
        return ""

# 原 generate_summary 更名為 _for_pair 並調整 Prompt
def generate_summary_for_pair(talk_text: str, ver_text: str, model: str, host: str) -> str:
    """使用 Ollama 為 talk 和 ver 配對生成摘要"""
    if (not talk_text or talk_text.isspace()) and (not ver_text or ver_text.isspace()):
        logging.warning("互動房和來賓訪談內容均為空或僅包含空白，無法生成摘要。")
        return "輸入內容為空或無效。"

    # 更新 Prompt，更強調整合 talk 和 ver
    prompt = f"""請**同時整合**以下「互動房內容」和「來賓訪談內容」，整理一份**詳細且側重於聽眾可能感興趣之資訊**的**繁體中文**摘要。

**重點歸納項目（請務必同時涵蓋兩部分內容中的相關資訊）：**
1.  **涉及國家/地區：**
2.  **店家/場所名稱：**
3.  **玩法/活動描述：**
4.  **費用/價格資訊（含幣別）：**
5.  **整體評價/心得/建議：**
6.  **主要話題/事件：**
7.  **其他重要資訊：**


**任務要求：**
*   摘要**必須均衡地**反映「互動房」和「來賓訪談」兩部分的重點，不可偏廢。
*   請**避免過於簡略**，盡力捕捉與上述項目相關的原文細節。
*   摘要應語意連貫、邏輯清晰，並**務必使用流暢的繁體中文**書寫。

--- 互動房內容 ---
{talk_text.strip()}

--- 來賓訪談內容 ---
{ver_text.strip()}

---
請根據以上要求，開始生成詳細且聚焦的繁體中文摘要："""

    try:
        logging.info(f"準備將配對內容傳送至 Ollama ({model} at {host}) 進行摘要生成...")
        client = ollama.Client(host=host)
        response = client.chat(
             model=model,
             messages=[{'role': 'user', 'content': prompt}],
             options={'temperature': 0.5}
        )
        logging.info(f"Ollama 已成功回應。")
        summary = response['message']['content']
        return summary.strip()
    except ollama.ResponseError as e:
         logging.error(f"Ollama API 回應錯誤: {e.status_code} - {e.error}")
         if "model not found" in str(e.error).lower():
             logging.error(f"錯誤：模型 '{model}' 未在 Ollama 中找到。請確認模型已下載並可用。")
         return f"Ollama API 錯誤: {e.error}"
    except Exception as e:
        logging.error(f"呼叫 Ollama API 時發生未知錯誤: {e}")
        try:
            ollama.ps(host=host)
        except Exception as conn_err:
             logging.error(f"無法連接到 Ollama 服務於 {host}。請確認 Ollama 服務正在運行且網路連線正常。錯誤: {conn_err}")
        return f"生成摘要時發生未知錯誤: {e}"

# 新增: 為單一檔案生成摘要的函數
def generate_summary_for_single(text: str, filename: str, model: str, host: str) -> str:
    """使用 Ollama 為單一檔案生成摘要"""
    if not text or text.isspace():
        logging.warning(f"檔案 {filename} 內容為空或僅包含空白，無法生成摘要。")
        return "輸入內容為空或無效。"

    prompt = f"""請根據以下提供的「{filename}」檔案內容，整理一份**詳細且側重於聽眾可能感興趣之資訊**的**繁體中文**摘要。

**重點歸納項目（請盡力捕捉並清晰呈現）：**
1.  **涉及國家/地區：**
2.  **店家/場所名稱：**
3.  **玩法/活動描述：**
4.  **費用/價格資訊（含幣別）：**
5.  **整體評價/心得/建議：**
6.  **主要話題/事件：**
7.  **其他重要資訊：**


**任務要求：**
*   摘要**必須**涵蓋文本中與上述重點項目相關的資訊。
*   請**避免過於簡略**，盡力捕捉與上述項目相關的原文細節。
*   摘要應語意連貫、邏輯清晰，並**務必使用流暢的繁體中文**書寫。

--- 檔案內容 ({filename}) ---
{text.strip()}

---
請根據以上要求，開始生成詳細且聚焦的繁體中文摘要："""

    try:
        logging.info(f"準備將單一檔案 ({filename}) 內容傳送至 Ollama ({model} at {host}) 進行摘要生成...")
        client = ollama.Client(host=host)
        response = client.chat(
             model=model,
             messages=[{'role': 'user', 'content': prompt}],
             options={'temperature': 0.5}
        )
        logging.info(f"Ollama 已成功回應。")
        summary = response['message']['content']
        return summary.strip()
    except ollama.ResponseError as e:
         logging.error(f"Ollama API 回應錯誤: {e.status_code} - {e.error}")
         if "model not found" in str(e.error).lower():
             logging.error(f"錯誤：模型 '{model}' 未在 Ollama 中找到。請確認模型已下載並可用。")
         return f"Ollama API 錯誤: {e.error}"
    except Exception as e:
        logging.error(f"呼叫 Ollama API 時發生未知錯誤: {e}")
        try:
            ollama.ps(host=host)
        except Exception as conn_err:
             logging.error(f"無法連接到 Ollama 服務於 {host}。請確認 Ollama 服務正在運行且網路連線正常。錯誤: {conn_err}")
        return f"生成摘要時發生未知錯誤: {e}"

def main():
    """主執行函數"""
    logging.info("腳本開始執行...")
    script_dir = Path(__file__).parent
    input_dir = (script_dir / INPUT_DIR).resolve()
    output_dir = (script_dir / OUTPUT_DIR).resolve()

    logging.info(f"腳本目錄: {script_dir}")
    logging.info(f"輸入資料夾 (解析後): {input_dir}")
    logging.info(f"輸出資料夾 (解析後): {output_dir}")
    logging.info(f"使用模型: {MODEL_NAME}")
    logging.info(f"Ollama Host: {OLLAMA_HOST}")

    output_dir.mkdir(parents=True, exist_ok=True)

    # 獲取需要處理的檔案列表
    process_items = find_files_to_process(input_dir)

    if not process_items:
        logging.warning(f"未在資料夾 {input_dir} 中找到任何符合命名規則 (S3EPXXX...txt) 的檔案。")
        return

    total_items = len(process_items)
    processed_count = 0
    skipped_count = 0 # 新增: 計數跳過的項目
    for item in process_items:
        processed_count += 1
        identifier = item['id']
        item_type = item['type']

        # --- 新增：檢查輸出檔案是否已存在 ---
        expected_output_filename = output_dir / f"{identifier}_摘要.txt"
        if expected_output_filename.exists():
            logging.info(f"項目 {processed_count}/{total_items}: ID {identifier} 的摘要檔案已存在 ({expected_output_filename.name})，跳過處理。")
            skipped_count += 1
            continue # 跳到下一個項目
        # --- 檢查結束 ---

        logging.info(f"--- 開始處理項目 {processed_count}/{total_items}: ID {identifier} (類型: {item_type}) ---")

        summary = ""
        if item_type == 'pair':
            talk_path = item['talk']
            ver_path = item['ver']
            logging.info(f"讀取檔案: {talk_path.name} 和 {ver_path.name}")
            talk_content = read_file_content(talk_path)
            ver_content = read_file_content(ver_path)
            if not talk_content and not ver_content:
                logging.warning(f"配對 {identifier} 的兩個檔案都無法讀取或為空，跳過此項目。")
                continue
            logging.info(f"[{identifier}] 準備呼叫 Ollama 為配對檔案生成摘要...")
            summary = generate_summary_for_pair(talk_content, ver_content, MODEL_NAME, OLLAMA_HOST)

        elif item_type == 'single':
            single_path = item['path']
            logging.info(f"讀取檔案: {single_path.name}")
            single_content = read_file_content(single_path)
            if not single_content:
                logging.warning(f"檔案 {single_path.name} 無法讀取或為空，跳過此項目。")
                continue
            logging.info(f"[{identifier}] 準備呼叫 Ollama 為單一檔案 ({single_path.name}) 生成摘要...")
            summary = generate_summary_for_single(single_content, single_path.name, MODEL_NAME, OLLAMA_HOST)

        logging.info(f"[{identifier}] Ollama 處理完成。準備寫入檔案...")

        # 檢查摘要是否包含錯誤訊息或無效
        if not summary or "錯誤:" in summary or "Ollama API" in summary or "生成摘要時發生" in summary or "輸入內容為空或無效" in summary:
            logging.error(f"[{identifier}] 生成摘要失敗或內容無效，請檢查日誌。摘要內容預覽: {summary[:200]}..." if summary else "摘要為空")
            # 可以在這裡選擇是否創建一個空的或包含錯誤訊息的摘要檔
            summary_content = f"{identifier}\n\n摘要生成失敗，請檢查腳本執行日誌。"
        else:
            logging.info(f"[{identifier}] 摘要生成成功。")
            # 為成功生成的摘要加上標題
            summary_content = f"{identifier}\n\n{summary}"

        # 使用之前檢查過的檔名變數
        output_filename = expected_output_filename
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            logging.info(f"摘要內容已成功寫入至: {output_filename}")
        except Exception as e:
            logging.error(f"寫入摘要檔案 {output_filename} 時發生錯誤: {e}")

        logging.info(f"--- 完成處理項目 {processed_count}/{total_items}: ID {identifier} ---")

    logging.info(f"所有項目處理完畢，共處理 {total_items} 個項目，其中 {skipped_count} 個項目因摘要已存在而被跳過。腳本執行結束。") # 更新結束訊息

if __name__ == "__main__":
    main() 