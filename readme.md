# 肥宅老司機 X Ollama 文件摘要腳本

本專案包含一個 Python 腳本 (`src/main.py`)，用於讀取指定資料夾中的 `talk` 和 `Ver` 文字檔案，將其內容合併（若兩者皆存在），並使用本地執行的 Ollama `gemma3:27b` 模型，根據預設的重點項目，生成詳細的**繁體中文**摘要。若僅找到單一檔案 (talk 或 ver)，也會單獨為其生成摘要。

此外，還包含一個輔助腳本 (`src/combine_summaries.py`)，用於將 `output` 資料夾中生成的摘要檔案合併成單一的 Markdown 格式檔案。

## 功能

### 主要摘要腳本 (`main.py`)

1.  **自動配對與單檔處理**：自動查找輸入資料夾中符合命名規則 (`S3EPXXX_talk.txt` 和 `S3EPXXX_Ver.txt`) 的檔案。若找到配對則合併處理，若僅找到其一則單獨處理。
2.  **內容合併**：若找到配對，將 talk 和 ver 檔案的內容合併為單一文字，並加入標示區分來源。
3.  **詳細摘要生成**：透過本地 Ollama 服務 (預設 `http://localhost:11434`) 和指定的模型 (`gemma3:27b`)，針對合併後或單一檔案的內容，根據預設的重點歸納項目（如涉及國家/地區、店家、玩法、費用、評價、主要話題等），生成詳細的繁體中文摘要。
4.  **輸出儲存**：將生成的摘要儲存到 `output` 資料夾，檔名格式為 `S3EPXXX_摘要.txt`。
5.  **跳過已存在摘要**：在處理每一集之前，會檢查 `output` 資料夾中是否已存在對應的 `S3EPXXX_摘要.txt` 檔案。如果檔案已存在，則會跳過該集，節省重複處理的時間。
6.  **錯誤處理**：包含基本的檔案讀取和 Ollama API 呼叫錯誤處理及日誌記錄。
7.  **編碼處理**：嘗試使用 UTF-8 讀取檔案，若失敗則回退至 CP950 (適用於部分 Windows 環境下的 Big5 編碼)。

### 摘要合併腳本 (`combine_summaries.py`)

1.  **讀取摘要**：讀取 `output` 資料夾中的所有 `_摘要.txt` 檔案。
2.  **按集數排序**：從檔案名中提取集數編號 (例如 `S3EPXXX` 中的 `XXX`)，並根據**數字大小**對所有找到的摘要檔案進行排序（從最小集數到最大集數）。
3.  **Markdown 格式化**：將每個摘要檔案的內容前加上以檔案名（例如 `S3EPXXX_摘要`）為標題的 Markdown 二級標頭 (`##`)，並在每個摘要後添加分隔線 (`---`)。
4.  **合併輸出**：將所有**按集數排序並格式化**後的摘要內容合併，並寫入到 `final_output` 資料夾下的 `combined_summaries.txt` 檔案中。此格式有助於後續如 RAG 等應用的資料處理。
5.  **自動創建目錄**：如果 `final_output` 資料夾不存在，腳本會自動創建它。

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

## 使用方式與測試

### 1. 測試生成單集摘要 (`main.py`) 與跳過功能

*   **準備工作**：
    *   確保您的 Ollama 服務正在執行且 `gemma3:27b` 模型已下載。
    *   確保您的 `faty_talk` 資料夾 (或您在 `main.py` 中設定的 `INPUT_DIR`) 中有 `S3EPXXX_talk.txt` 或 `S3EPXXX_Ver.txt` 檔案。
    *   **（可選）測試跳過功能**：如果您想測試跳過功能，可以手動刪除 `output` 資料夾中的**部分** `S3EPXXX_摘要.txt` 檔案，保留一些已有的摘要檔。
*   **執行腳本**：
    1.  開啟終端機，進入專案根目錄 (例如 `S3EP201_204`)。
    2.  啟用虛擬環境 (如果尚未啟用):
        ```bash
        # Windows
        .venv\Scripts\activate
        # macOS/Linux
        source .venv/bin/activate
        ```
    3.  執行主腳本:
        ```bash
        python main.py
        ```
*   **觀察結果**：
    *   注意終端機的輸出。對於 `output` 資料夾中**已存在**摘要的集數，您應該會看到類似 `... 的摘要檔案已存在 ...，跳過處理。` 的訊息。
    *   對於 `output` 資料夾中**不存在**摘要的集數（或您剛剛刪除的），腳本會讀取輸入檔案，呼叫 Ollama 生成摘要，並將新生成的 `S3EPXXX_摘要.txt` 存入 `output` 資料夾。
    *   檢查 `output` 資料夾，確認之前不存在的摘要檔案現在已經生成。

### 2. 測試合併所有摘要 (`combine_summaries.py`) 與排序功能

*   **準備工作**：
    *   確保 `output` 資料夾中有多個 `S3EPXXX_摘要.txt` 檔案（可以透過執行上一步的 `main.py` 生成）。確保這些檔案的集數編號 `XXX` 有所不同，以便測試排序。
*   **執行腳本**：
    1.  確保您仍在啟用虛擬環境的終端機中，並且位於專案根目錄。
    2.  執行合併腳本：
        ```bash
        python combine_summaries.py
        ```
*   **觀察結果**：
    *   終端機應顯示成功合併的摘要數量，並提示輸出檔案的路徑 (`final_output/combined_summaries.txt`)。
    *   打開 `final_output/combined_summaries.txt` 檔案。
    *   **檢查排序**：瀏覽檔案內容，確認各個摘要是按照 `## S3EPXXX_摘要` 標頭中的集數 `XXX` **從數字小到大**排列的。例如，`## S3EP9_摘要` 應該出現在 `## S3EP10_摘要` 之前，`## S3EP199_摘要` 應該出現在 `## S3EP200_摘要` 之前。
    *   **檢查格式**：確認每個摘要前有 `##` 標頭，摘要內容緊隨其後，且每個摘要之間有 `---` 分隔線。

## 注意事項

*   **Ollama 連線**: 腳本預設連接 `http://localhost:11434`。如果您的 Ollama 服務運行在不同地址或端口，請修改 `src/main.py` 中的 `OLLAMA_HOST` 變數。
*   **模型名稱**: 腳本預設使用 `gemma3:27b`。如果您想使用其他已下載的模型，請修改 `src/main.py` 中的 `MODEL_NAME` 變數。
*   **檔案命名**: 輸入檔案必須嚴格遵守 `S3EPXXX_talk.txt` 和 `S3EPXXX_Ver.txt` 的格式 (大小寫不敏感)，其中 `XXX` 為集數編號。
*   **處理時間**: 根據您的硬體配置和文本長度，使用 `gemma3:27b` 生成摘要可能需要較長時間。腳本會記錄開始和結束處理每個檔案對的時間。
*   **大量檔案**: 如果檔案數量非常多，處理時間會相應增加。
*   **輸入路徑**: `INPUT_DIR = Path("..")` 這行設定輸入資料夾為 `src` 的上一層目錄 (即專案根目錄 `S3EP201_204`)。請確保您的 `.txt` 檔案放在這裡。
*   **輸出路徑**: `OUTPUT_DIR = Path("../output")` 設定輸出資料夾為 `src` 上一層目錄下的 `output` 資料夾 (即 `S3EP201_204/output`)。

### 3. 使用場景與進階應用

*   **RAG 資料庫整合**：
    *   將生成的摘要檔案作為 RAG（檢索增強生成）系統的資料庫來源。
    *   可與「館長」資料庫（https://ai.ncurator.com/）搭配使用，進行更深入的分析。
*   **模型選擇**：
    *   **本地部署**：使用 Ollama 的 `gemma3:27b` 模型。
    *   **線上服務**：可選擇 Siliconflow 的 Deepseek Chat 模型（https://cloud.siliconflow.cn/i/8wkTP6UJ）。
*   **進階設置**：
    *   在「館長」資料庫的高級設置中選擇中文模型。
    *   新用戶註冊 Siliconflow 可獲得 2000 萬 Tokens 免費額度。

---
最後更新：2025/04/28


製作者: 波尼

聯絡信箱: liupony2000@gmail.com

特別感謝 肥宅老司機優質好節目
收聽連結：https://open.firstory.me/user/fattyinsider/episodes
特別感謝 館長Yoan 提供好用的RAG資料庫
資料庫連結：https://ai.ncurator.com/


---
如果您喜歡 肥宅老司機 X Ollama 文件摘要腳本
可以斗內到以下地址支持創作：
USDT (TRC20)
TExxw25EaPKZdKr9uPJT8MLV2zHrQBbhQg
多幣錢包
liupony2000.x