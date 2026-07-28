# 原始公告翻譯

## 原文翻譯

原作者 @slvDev 的公告傳達四件事：

1. 一個 28.9M 儲存參數量的 LLM 正在約 8 美元的 ESP32 上運行，並把
   生成的故事寫到螢幕上。
2. 整個流程都在晶片本地完成，沒有把資料送到 server。
3. `~100x` 比較的是 2023 年同類 ESP32 實驗的儲存參數量，不是能力、
   品質或速度強 100 倍。
4. 這項工作受到 Karpathy 的 `llama2.c` 與 Google Per-Layer
   Embeddings（逐層嵌入）啟發；後者讓大型權重表可留在 Flash，而不是
   全部放進 RAM。

為方便逐句核對，原文中的關鍵短語包括：「28.9M LLM」、「fully on the
chip」、「nothing goes to a server」、「~100x bigger」與
「per-layer embeddings」。完整原文請直接閱讀
[原始 X 公告](https://x.com/slvdev/status/2080322138410524737)。

## 譯註

- 公告的「writing a story」對應 TinyStories 文字生成，不代表對話式助理。
- `~100x` 在 upstream `RESULTS.md` 中被更精確地限定為約 110 倍的
  stored parameter count，比較對象是先前獨立的 260K-parameter
  ESP32 實驗。
- `llama2.c` 是靈感與先前工作脈絡；upstream
  [`RESULTS.md`](https://github.com/slvDev/esp32-ai/blob/74744182329f08d7a1badc97e47576ef527532a0/RESULTS.md#remaining-limitations)
  明確說明其程式碼、模型、checkpoint 與方法並非衍生自 `llama2.c`。
- 公告沒有聲稱 microphone、BLE、BTHome、Home Assistant 或 swarm
  已包含在 upstream 實作中。

## 尚未驗證

本頁只核對公告文字與 pinned repository。公告中的裝置效能仍是
upstream reported；本倉庫尚未完成 R5 locally reproduced。

## 來源 receipt

- upstream repository：[`slvDev/esp32-ai`](https://github.com/slvDev/esp32-ai)
- inspected commit：[`74744182`](https://github.com/slvDev/esp32-ai/tree/74744182329f08d7a1badc97e47576ef527532a0)
- 原始作者：Viacheslav Sierbov（slvDev）
- 原始頁面：[X announcement by @slvDev](https://x.com/slvdev/status/2080322138410524737)
- repository license：[MIT License](../../LICENSE)
