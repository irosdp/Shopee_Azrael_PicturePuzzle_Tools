# 蝦皮上架拼圖神器 (Shopee Puzzle Tool - Azrael Edition)

![License](https://img.shields.io/badge/license-GPLv3-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-yellow.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

**專為蝦皮賣家打造的高效圖片處理工具，結合長圖拼接、智慧裁切與 Azrael 看板娘專屬主題。**

這款工具旨在解決蝦皮（Shopee）對於商品圖片的嚴格限制（寬度、高度比例、檔案大小、張數上限）。它允許賣家將淘寶/天貓等平台的長條商品詳情圖，透過視覺化的拖曳與點擊操作，快速重組並輸出成符合蝦皮規範的 12 張圖片。

---

## ✨ 核心功能 (Features)

### 🧩 智慧拼接與裁切
- **自動縮放**：強制將圖片統一為寬度 800px，符合蝦皮最佳瀏覽規範。
- **長圖拼接**：支援多張圖片拖曳匯入，自動垂直拼接成一張長卷軸。
- **智慧分割**：自動計算高度（限制單張高 1600px），確保長寬比符合 0.5~32 的規範。
- **張數監控**：即時計算輸出張數，若超過 12 張會以紅字警告。

### ✂️ 所見即所得 (WYSIWYG) 編輯器
- **複數選取**：在黑色區域拖曳即可建立新的選取範圍（保留區）。
- **點擊分割 (Split-on-Click)**：在選取區內點擊左鍵，瞬間將區塊一分為二，方便剔除中間廣告。
- **拖曳移動**：按住選取區即可上下移動位置。
- **右鍵刪除**：不需要的區塊，按右鍵直接移除。

### 🖥️ 現代化介面與 UX
- **Azrael 專屬主題**：內建「Azrael Deep (深粉/暗黑)」與「Azrael Pale (淡粉/夢幻)」兩種高質感配色。
- **多欄位縮圖預覽**：右側 MiniMap 支援自動折行顯示，超長圖片也能一覽無遺。
- **動態 Splitter**：預覽區與工作區寬度可自由拖曳調整。
- **記憶功能**：自動記住上次開啟圖片的資料夾路徑。

### 🎨 Azrael 看板娘整合
- 程式背景嵌入淡化處理的 Azrael 看板娘，工作時也能被療癒。
- 包含專屬應用程式圖示與關於視窗。

---

## 📸 介面預覽 (Screenshots)

<img width="1920" height="1049" alt="screenshot" src="https://github.com/user-attachments/assets/2ae7a90b-9f77-4ee6-841a-e1b9797dff8f" />

---

## 🚀 安裝與執行 (Installation)

### 方法一：下載執行檔 (Recommended)
前往 [Releases](./releases) 頁面下載最新打包好的 `.exe` 檔案，無需安裝 Python 即可直接執行。

### 方法二：從原始碼執行
若您想自行修改或編譯，請確保已安裝 Python 3.9+。

1. **Clone 專案**
   ```bash
   git clone https://github.com/YourUsername/Shopee-Puzzle-Tool-Azrael.git
   cd Shopee-Puzzle-Tool-Azrael
