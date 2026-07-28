# 第三方聲稱與 upstream 邊界

本頁只做來源分離，不是 @ardchain 文章的完整翻譯，也不認可其硬體與
flashing instructions。

## 來源矩陣

| Claim | Source class | Pinned upstream state |
|---|---|---|
| 28.9M 儲存參數量 TinyStories model 在 ESP32-S3 本地生成文字 | 原文翻譯／upstream implementation | `README.md`、`RESULTS.md` 與 firmware source 有對應 |
| 約 9.5 tok/s 端到端吞吐量 | upstream reported | 本倉庫尚未 locally reproduced |
| I2S microphone capture | 第三方聲稱 | pinned upstream 未實作 |
| voice intent parsing／structured JSON intent | 第三方聲稱 | pinned upstream 是 TinyStories 生成模型，未實作 intent classifier |
| BLE macro、BTHome payload、Home Assistant discovery | 第三方聲稱 | pinned upstream 未實作 |
| distributed ESP32 swarm | 第三方聲稱 | pinned upstream 未實作 |
| `LLM_Init()`、`I2S_Record_Voice()` | 第三方聲稱 | 文章示意 pseudocode，不是 upstream symbols |
| `0x400000` model flash address | 第三方聲稱 | 與 upstream `0x110000` 流程不同 |

## 原文翻譯：@slvDev 的範圍

@slvDev 的原始公告與 repository 展示的是：28.9M 儲存參數量、
TinyStories-domain 文字生成、on-chip inference、Per-Layer Embeddings
與 ESP32-S3 記憶體階層。模型輸出是故事文字，不是可安全執行的
structured intent。

## 第三方聲稱：@ardchain 的延伸

@ardchain 的文章把 upstream 架構延伸成
`Listen → Parse → Route → Execute` 的 physical swarm，並加入 I2S
microphone、wake word、voice intent、BLE、BTHome 與 Home Assistant。
這些內容可以當作另一個產品構想，但不在 inspected upstream commit
`74744182329f08d7a1badc97e47576ef527532a0` 內。

文章中的 C++ 片段使用 `LLM_Init()`、`I2S_Record_Voice()`、
`Detect_Wake_Word()` 與 `BLE_Send_Macro()`。在 pinned repository 中找不到
這些 symbols，因此只能視為 pseudocode。

文章建議把 model 寫到 `0x400000`；upstream 的
`firmware/esp32_llm/partitions.csv` 與官方操作文件則使用 `0x110000`。
不能混用兩套位址或 binary。

## 譯註：安全與能力

TinyStories generator 不能可靠地把自然語言轉成可執行 intent。即使未來
另做 voice／BLE 系統，也需要 deterministic schema validation、權限邊界、
明確的人或 policy gate 與 execution receipt；不能因模型在本地執行就
推定輸出安全。

## 尚未驗證

本倉庫沒有 build 或測試 @ardchain 描述的任何 extension，也沒有核對其
binary、wiring 或 Home Assistant 行為。該文章所有這類結果均維持
`第三方聲稱`，不得標成 locally reproduced。

## 來源 receipt

- upstream repository：[`slvDev/esp32-ai`](https://github.com/slvDev/esp32-ai)
- inspected commit：[`74744182`](https://github.com/slvDev/esp32-ai/tree/74744182329f08d7a1badc97e47576ef527532a0)
- 原始作者：Viacheslav Sierbov（slvDev）
- upstream source：[`README.md` — What it does, and what it does not](https://github.com/slvDev/esp32-ai/blob/74744182329f08d7a1badc97e47576ef527532a0/README.md#what-it-does-and-what-it-does-not)
- third-party source：[@ardchain X article](https://x.com/ardchain/status/2081775980650139929)
- license：[MIT License](../../LICENSE)
