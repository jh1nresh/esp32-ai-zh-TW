# 繁體中文術語表

下列譯法是本倉庫的固定用語。

| English | zh-TW canonical term | 使用說明 |
|---|---|---|
| stored parameters | 儲存參數量 | 描述保存的參數總數，不等於能力或同時載入 fast memory 的數量 |
| inference | 推論 | 模型由輸入產生輸出的執行階段 |
| firmware | 韌體 | 在 ESP32-S3 上 build／flash／run 的程式 |
| flash | Flash 快閃記憶體 | 非揮發儲存；保留英文 Flash 以對應 upstream |
| PSRAM | PSRAM | 外部 pseudo-static RAM，不翻譯縮寫 |
| SRAM | SRAM | 晶片內快速 static RAM，不翻譯縮寫 |
| memory-mapped | 記憶體映射 | 由 address space 直接讀取 Flash 資料 |
| Per-Layer Embeddings | Per-Layer Embeddings（逐層嵌入） | 第一次出現保留英文與中文，之後可寫 PLE |
| quantization | 量化 | 把權重轉為較低 bit-width 的表示 |
| output head | 輸出頭 | 把 hidden state 映射到 vocabulary logits |
| end-to-end throughput | 端到端吞吐量 | 包含使用者可見輸出等完整路徑 |
| compute-only throughput | 純運算吞吐量 | 只計 model step 的運算路徑 |
| checkpoint | checkpoint／訓練檢查點 | 訓練保存的模型 state；filenames 不翻譯 |
| artifact | artifact／產物 | export 或 build 生成且可用 hash 識別的檔案 |
| receipt | receipt／驗證紀錄 | 日期、環境、命令、exit code、輸出、hash 與差異 |
| upstream | upstream／上游 | 原始 `slvDev/esp32-ai` repository |

## 禁止的語義替換

- `stored parameters` 不得簡化成「模型能力」。
- `~100x parameters` 不得翻成「強 100 倍」。
- `bandwidth-only ceiling` 不得翻成「實際推論速度」。
- `upstream reported` 不得省略成無來源的「實測」。
- `third-party claim` 不得歸因給 upstream 作者。

## 來源 receipt

- upstream repository：[`slvDev/esp32-ai`](https://github.com/slvDev/esp32-ai)
- inspected commit：[`74744182`](https://github.com/slvDev/esp32-ai/tree/74744182329f08d7a1badc97e47576ef527532a0)
- 原始作者：Viacheslav Sierbov（slvDev）
- 原始頁面：[`README.md` — The numbers](https://github.com/slvDev/esp32-ai/blob/74744182329f08d7a1badc97e47576ef527532a0/README.md#the-numbers)
- license：[MIT License](../../LICENSE)
