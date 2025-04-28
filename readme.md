# 肥宅老司機 X Ollama 文件摘要腳本

本專案包含一個 Python 腳本，用於讀取指定資料夾中的 `talk` 和 `Ver` 文字檔案，將其內容合併（若兩者皆存在），並使用本地執行的 Ollama `gemma3:27b` 模型，根據預設的重點項目，生成詳細的**繁體中文**摘要。若僅找到單一檔案 (talk 或 ver)，也會單獨為其生成摘要。

## 功能

1.  **自動配對與單檔處理**：自動查找輸入資料夾中符合命名規則 (`S3EPXXX_talk.txt` 和 `S3EPXXX_Ver.txt`) 的檔案。若找到配對則合併處理，若僅找到其一則單獨處理。
2.  **內容合併**：若找到配對，將 talk 和 ver 檔案的內容合併為單一文字，並加入標示區分來源。
3.  **詳細摘要生成**：透過本地 Ollama 服務 (預設 `http://localhost:11434`) 和指定的模型 (`gemma3:27b`)，針對合併後或單一檔案的內容，根據預設的重點歸納項目（如涉及國家/地區、店家、玩法、費用、評價、主要話題等），生成詳細的繁體中文摘要。
4.  **輸出儲存**：將生成的摘要儲存到 `output` 資料夾，檔名格式為 `S3EPXXX_摘要.txt`。
5.  **錯誤處理**：包含基本的檔案讀取和 Ollama API 呼叫錯誤處理及日誌記錄。
6.  **編碼處理**：嘗試使用 UTF-8 讀取檔案，若失敗則回退至 CP950 (適用於部分 Windows 環境下的 Big5 編碼)。

## 設定步驟

1.  **安裝 Python**: 確保您的系統已安裝 Python 3.8 或更高版本。
2.  **安裝 Ollama**:
    *   前往 [Ollama 官方網站](https://ollama.com/) 下載並安裝 Ollama。
    *   執行 Ollama 並下載所需的模型：
        ```bash
        ollama pull gemma3:27b
        ```
    *   確保 Ollama 服務正在背景執行。
3.  **建立虛擬環境**:
    *   在專案根目錄 (包含 `src`, `requirements.txt` 的目錄) 開啟終端機。
    *   執行以下指令建立虛擬環境：
        ```bash
        python -m venv .venv
        ```
4.  **啟用虛擬環境**:
    *   **Windows (PowerShell/CMD)**:
        ```bash
        .venv\Scripts\activate
        ```
    *   **macOS/Linux (Bash/Zsh)**:
        ```bash
        source .venv/bin/activate
        ```
    *   啟用成功後，終端機提示符前會出現 `(.venv)`。
5.  **安裝依賴**:
    *   在已啟用虛擬環境的終端機中執行：
        ```bash
        pip install -r requirements.txt
        ```
6.  **準備輸入檔案**:
    *   將您的 `S3EPXXX_talk.txt` 和 `S3EPXXX_Ver.txt` 檔案放入專案根目錄（與 `src` 資料夾同層）。腳本預設會讀取此處的檔案。
    *   如果您想更改輸入資料夾，請修改 `src/main.py` 中的 `INPUT_DIR` 變數。目前設定為 `Path("..")`，表示 `src` 的上一層目錄。

## 使用方式

1.  **確保 Ollama 正在執行** 且 `gemma3:27b` 模型已下載。
2.  **啟用虛擬環境** (如果尚未啟用)。
3.  **執行腳本**:
    *   在專案根目錄的終端機中，切換到 `src` 資料夾：
        ```bash
        cd src
        ```
    *   執行主腳本：
        ```bash
        python main.py
        ```
4.  **查看結果**:
    *   腳本執行時會在終端機輸出處理進度和日誌。
    *   處理完成後，生成的摘要檔案會儲存在專案根目錄下的 `output` 資料夾中。

## 注意事項

*   **Ollama 連線**: 腳本預設連接 `http://localhost:11434`。如果您的 Ollama 服務運行在不同地址或端口，請修改 `src/main.py` 中的 `OLLAMA_HOST` 變數。
*   **模型名稱**: 腳本預設使用 `gemma3:27b`。如果您想使用其他已下載的模型，請修改 `src/main.py` 中的 `MODEL_NAME` 變數。
*   **檔案命名**: 輸入檔案必須嚴格遵守 `S3EPXXX_talk.txt` 和 `S3EPXXX_Ver.txt` 的格式 (大小寫不敏感)，其中 `XXX` 為集數編號。
*   **處理時間**: 根據您的硬體配置和文本長度，使用 `gemma3:27b` 生成摘要可能需要較長時間。腳本會記錄開始和結束處理每個檔案對的時間。
*   **大量檔案**: 如果檔案數量非常多，處理時間會相應增加。
*   **輸入路徑**: `INPUT_DIR = Path("..")` 這行設定輸入資料夾為 `src` 的上一層目錄 (即專案根目錄 `S3EP201_204`)。請確保您的 `.txt` 檔案放在這裡。
*   **輸出路徑**: `OUTPUT_DIR = Path("../output")` 設定輸出資料夾為 `src` 上一層目錄下的 `output` 資料夾 (即 `S3EP201_204/output`)。

---
最後更新：2025/04/28
