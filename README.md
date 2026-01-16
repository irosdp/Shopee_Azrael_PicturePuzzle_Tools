# 蝦皮上架拼圖神器 (Shopee Puzzle Tool - Azrael Edition)

![License](https://img.shields.io/badge/license-GPLv3-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-yellow.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Version](https://img.shields.io/badge/version-v1.3-pink.svg)

**專為蝦皮賣家打造的高效圖片處理工具，結合長圖拼接、智慧裁切與 Azrael 看板娘專屬主題。**

這款工具旨在解決蝦皮（Shopee）對於商品圖片的嚴格限制（寬度、高度比例、檔案大小、張數上限）。它允許賣家將淘寶/天貓等平台的長條商品詳情圖，透過視覺化的拖曳與點擊操作，快速重組並輸出成符合蝦皮規範的 12 張圖片。

---

## ✨ 核心功能 (Features)

### 🧩 智慧拼接與裁切
- **自動縮放**：強制將圖片統一為寬度 800px，符合蝦皮最佳瀏覽規範。
- **無縫長圖**：支援多張圖片拖曳匯入，自動垂直拼接成一張長卷軸。
- **智慧分割**：自動計算高度（限制單張高 1600px），確保長寬比符合 0.5~32 的規範。
- **數據監控**：即時計算輸出張數與**需刪減的高度像素**，精準掌握修圖進度。

### ✂️ 所見即所得 (WYSIWYG) 編輯器
- **複數選取**：在黑色區域拖曳即可建立新的選取範圍（保留區）。
- **點擊分割 (Split-on-Click)**：在選取區內**點擊左鍵**，瞬間將區塊一分為二，方便剔除中間廣告。
- **拖曳移動**：按住選取區即可上下移動位置。
- **右鍵刪除**：不需要的區塊，按右鍵直接移除。
- **重製選取區**：一鍵重置所有裁切框，恢復全選狀態。

### 📂 檔案與列表管理 (New in v1.3)
- **智慧排序**：
    - **依名稱排序**：依照檔名 (A-Z) 排列。
    - **依日期排序**：依照修改時間 (舊→新) 排列。
- **鍵盤支援**：支援使用 **`Delete` 鍵** 快速移除列表中的圖片。
- **記憶功能**：
    - 自動記憶上次開啟與輸出的資料夾路徑。
    - **記憶前綴字**：自動記住上次使用的「描述圖前綴」與「主圖前綴」，免去重複輸入。
- **防覆蓋機制**：輸出時若檔名重複，自動更名 (如 `_1.jpg`)，保護舊檔案。

### 🖥️ 現代化介面與 UX
- **Azrael 專屬主題**：內建「Azrael Deep (深粉/暗黑)」與「Azrael Pale (淡粉/夢幻)」兩種高質感配色。
- **看板娘背景**：工作區右下角嵌入淡化的 Azrael 看板娘，隨視窗大小自動調整。
- **多欄位縮圖預覽**：右側 MiniMap 支援自動折行顯示，超長圖片也能一覽無遺。
- **動態 Splitter**：預覽區與工作區寬度可自由拖曳調整。

---

## 📸 介面預覽 (Screenshots)

*(請在此處上傳您的軟體截圖，例如主畫面與關於視窗)*

---

## 🚀 下載與執行 (Installation)

### 方法一：下載執行檔 (Recommended)
前往 [Releases](../../releases) 頁面下載最新打包好的 `.exe` 檔案，無需安裝 Python 即可直接執行。

### 方法二：從原始碼執行
若您想自行修改或編譯，請確保已安裝 Python 3.9+。

1. **Clone 專案**
   ```bash
   git clone https://github.com/YourUsername/Shopee-Puzzle-Tool-Azrael.git
   cd Shopee-Puzzle-Tool-Azrael
