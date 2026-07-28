# 記憶體階層、量化與 Per-Layer Embeddings

## 原文翻譯：核心想法

ESP32-S3 N16R8 提供 512KB SRAM、8MB PSRAM 與 16MB Flash。一般做法若
要求模型所有權重都能從快速記憶體直接取得，容量會被 SRAM 限制。
upstream 的做法是把不同資料放到不同記憶體階層：大量、每次只讀少數
row 的資料留在 Flash；較常順序讀取的輸出頭在開機時 staged 到 PSRAM；
低延遲的運算狀態使用 SRAM。

```text
SRAM  -> 最快、最小：hot working state、cache 與低延遲運算
PSRAM -> 較大、較慢：staged output head、KV cache 與 scratch
Flash -> 最大、非揮發：量化 model artifact 與記憶體映射 PLE table
```

## 譯註：28.9M 為何能放進 16MB Flash

28.9M 是**儲存參數量**，不是 28.9M 個 fp32 參數同時放入 SRAM：

| 組成 | upstream 描述 | 執行時角色 |
|---|---:|---|
| dense core | 約 559K parameters | 執行 attention、FFN 與 PLE adapter；現行 polished firmware 的權重可保持 Flash-mapped XIP |
| tied embedding／output head | 約 3.1M parameters | 從 model artifact 載入並以 int8 staged 到 PSRAM |
| PLE lookup table | 約 25M parameters | 留在 Flash，依目前 token 與 layer 讀取少量 rows |

若所有 28.9M parameters 都是 fp32，光權重約需 115.6MB。4-bit 量化把每個
大型權重理想化為半個 byte；28.9M × 0.5 約為 14.45MB。實際格式還包含
header、fp16 group scales 與少量 fp32 norm：

- upstream reported：匯出 artifact 是 14,912,332 bytes；
- upstream reported：custom model partition 是 15,597,568 bytes；
- upstream reported：artifact 尚餘 685,236 bytes partition 空間。

因此「放得進 16MB Flash」指量化後的完整 artifact 能放入指定的 model
partition，不是 28.9M 個參數同時常駐 512KB SRAM。

## 譯註：Per-Layer Embeddings 如何工作

傳統 token embedding 通常在模型底部把 token ID 轉成一個向量。
Per-Layer Embeddings（逐層嵌入）則讓每一層都能取得與目前 token
對應的額外 embedding row。upstream 的 25M-parameter table 很大，但
每個 token 不會掃過整張表；它只做稀疏的 row lookup。

upstream README 描述 6-layer 設定每個 token 約讀 6 rows，合計約 450
bytes。這就是關鍵交換：用 Flash 容量保存很多 rows，只支付當前 token
真正索引到的少量讀取。

這些額外 rows 改善了 upstream TinyStories 實驗中的 coherence 與
perplexity，但不會自動擴大 dense core 的 reasoning、world knowledge
或 instruction-following 能力。

## 譯註：SRAM 圖示與現行 firmware 的細節

upstream README 用「SRAM 是 thinking core」解釋設計預算：dense core
被控制在約 559K parameters，使其規模符合極小 fast-memory 環境。
但 pinned `RESULTS.md` 也說明，polished firmware 實際量測後讓 core
weights 保持 Flash-mapped XIP；SRAM 仍負責 hot execution state。
這兩句分別是架構心智模型與目前實作細節，不應被寫成互相矛盾的
「全部 core weights 必定常駐 SRAM」。

同樣地，upstream firmware boot diagnostics 的 `head staged int8:
2.53 MB` 是 allocation 診斷；`RESULTS.md` 的 2.43MB 則描述每 token
讀取的 int8 weights。兩者不是同一個量測欄位。

## 能力邊界

- 模型領域是 TinyStories 短篇故事。
- 它不能可靠回答問題、遵循指令、寫程式或提供世界知識。
- 28.9M 儲存參數量不能換算成 28.9M dense model 的能力。
- 約 100 倍只比較儲存參數量，不是能力、速度或品質倍數。
- microphone、voice intent、BLE、BTHome、Home Assistant 與 swarm
  是第三方延伸構想，不是這個 upstream commit 的功能。

## 來源 receipt

- upstream repository：[`slvDev/esp32-ai`](https://github.com/slvDev/esp32-ai)
- inspected commit：[`74744182`](https://github.com/slvDev/esp32-ai/tree/74744182329f08d7a1badc97e47576ef527532a0)
- 原始作者：Viacheslav Sierbov（slvDev）
- 原始頁面：[`README.md` — Why it is hard, and how it fits anyway](https://github.com/slvDev/esp32-ai/blob/74744182329f08d7a1badc97e47576ef527532a0/README.md#why-it-is-hard-and-how-it-fits-anyway)
- 補充來源：[`RESULTS.md` — Headline](https://github.com/slvDev/esp32-ai/blob/74744182329f08d7a1badc97e47576ef527532a0/RESULTS.md#headline-the-deployable-config)
- license：[MIT License](../../LICENSE)
