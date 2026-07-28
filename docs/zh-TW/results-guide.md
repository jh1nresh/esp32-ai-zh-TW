# RESULTS 核心結果與限制導讀

本頁是 headline、on-chip generation 與 limitations 的快速導讀；完整
逐章繁中翻譯見 [`../../RESULTS.zh-TW.md`](../../RESULTS.zh-TW.md)。
所有結果均來自 upstream commit
`74744182329f08d7a1badc97e47576ef527532a0`，不是本倉庫實測。

## 原文翻譯：Headline

部署設定使用 vocab 32768、約 559K-parameter dense core、25M-parameter
PLE table、`d_model=96`、6 layers 與 `ple_dim=128`。upstream 以兩個
seeds 比較同 core 預算的模型：

- upstream reported：baseline 為 3.7M 儲存參數量，ppl 12.58。
- upstream reported：PLE 為 28.9M 儲存參數量，ppl 11.41，相對
  baseline 改善 0.098 nats／9.3% perplexity。
- upstream reported：`fatembed` 同為 28.9M 儲存參數量，ppl 11.94。

upstream 的結論是 PLE 在相同 dense-core 預算下優於 baseline，且
逐層注入優於只在底部加入同規模 embedding。這不表示 28.9M 儲存參數量
具有同等規模 dense model 的能力。

原文：
[`RESULTS.md` — Headline (the deployable config)](https://github.com/slvDev/esp32-ai/blob/74744182329f08d7a1badc97e47576ef527532a0/RESULTS.md#headline-the-deployable-config)

## 原文翻譯：On-chip generation

upstream reported：匯出的 model artifact 是 14,912,332 bytes，可放入
15,597,568-byte custom Flash partition，剩餘 685,236 bytes；application
位於另一個 1MB partition。

upstream reported：portable C runtime 在所有 32,768 logits 上與匯出的
PyTorch golden 相符，`max abs diff = 0.00001`。

upstream reported：ESP32-S3 上的 greedy generation 從
`Once upon a time` 開始，可生成連貫的 TinyStories 文字。

upstream reported：約 9.5 tok/s 端到端吞吐量；102.9ms/model step，
也就是純運算吞吐量 9.72 tok/s。這是 upstream 的裝置量測；尚未
locally reproduced。

原文：
[`RESULTS.md` — On-chip generation: complete model running](https://github.com/slvDev/esp32-ai/blob/74744182329f08d7a1badc97e47576ef527532a0/RESULTS.md#on-chip-generation-complete-model-running-2026-07-21)

## 譯註：如何讀效能數字

- `end-to-end throughput` 包含 viewer 實際看到的 serial output。
- `compute-only throughput` 只計 model step，因此數值略高。
- upstream reported：58 tok/s 是 bandwidth-only ceiling，不是實際推論速度。
- upstream reported：flash table 在 isolated bandwidth benchmark 中只佔
  per-token memory time 約 0.7%；這不等於 PLE 總推論 overhead 只有 0.7%。
- upstream 沒有提供本 repo 可直接下載的展示 `model.bin`，所以只 clone
  repository 不能重現上述數字。

## 原文翻譯：Remaining limitations

1. 現行 runtime 的 dot products 仍是 scalar，沒有使用 ESP32-S3 SIMD；
   output head 已受 PSRAM bandwidth 限制，所以 SIMD 單獨帶來的空間有限。
2. 模型領域仍是 TinyStories；world knowledge、arithmetic 與 multi-step
   reasoning 缺失，這個上限由 dense core 決定，不會因大型 table 消失。
3. 這是獨立工作。實際依賴是 TinyStories dataset 與 Google 公開的
   Gemma Per-Layer Embeddings 設計；`llama2.c` 與 DaveBben 的
   `esp32-llm` 只作為靈感／比較脈絡。
4. upstream 的新穎性主張很窄：把 Gemma-style Per-Layer Embeddings
   套用到 microcontroller 的 SRAM／Flash 階層，使儲存模型可大於
   fast-memory 容量。

原文：
[`RESULTS.md` — Remaining limitations](https://github.com/slvDev/esp32-ai/blob/74744182329f08d7a1badc97e47576ef527532a0/RESULTS.md#remaining-limitations)

## 尚未驗證

本倉庫目前只有 R0 source audit。訓練、export、host verification、
firmware compile、device generation 與 performance measurement 都沒有
本地 command output；詳見
[`reproduction-status.md`](reproduction-status.md)。

## 來源 receipt

- upstream repository：[`slvDev/esp32-ai`](https://github.com/slvDev/esp32-ai)
- inspected commit：[`74744182`](https://github.com/slvDev/esp32-ai/tree/74744182329f08d7a1badc97e47576ef527532a0)
- 原始作者：Viacheslav Sierbov（slvDev）
- 原始頁面：[`RESULTS.md`](https://github.com/slvDev/esp32-ai/blob/74744182329f08d7a1badc97e47576ef527532a0/RESULTS.md)
- license：[MIT License](../../LICENSE)
