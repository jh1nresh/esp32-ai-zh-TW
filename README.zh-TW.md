# esp32-ai 繁體中文翻譯與重現筆記

> 本倉庫是 slvDev/esp32-ai 的非官方繁體中文翻譯、技術解讀與重現紀錄。
> 原始專案作者為 Viacheslav Sierbov（slvDev），依 MIT License 使用。
> 如翻譯與英文原文有歧義，以 upstream 原文為準。
> 所有效能數字都必須標示為 upstream reported 或 locally reproduced。

翻譯基準是 [`slvDev/esp32-ai`](https://github.com/slvDev/esp32-ai) commit
[`74744182329f08d7a1badc97e47576ef527532a0`](https://github.com/slvDev/esp32-ai/tree/74744182329f08d7a1badc97e47576ef527532a0)。
英文入口與原始說明保留在 [`README.md`](README.md)；原始碼授權見
[`LICENSE`](LICENSE)。

## 十分鐘先讀

**它是什麼？** 這是一個在 ESP32-S3 N16R8 上離線生成 TinyStories
短篇故事的 28.9M 儲存參數量語言模型。它展示的是如何利用記憶體階層，
讓遠大於 SRAM 容量的模型資料留在 Flash 快閃記憶體中，並按 token
取用所需內容。

**它不是什麼？** 它不是通用助理、中文模型、語音助理、intent
classifier、BLE／BTHome／Home Assistant 節點或 ESP32 swarm。上游明確
說明它不能可靠地回答問題、遵循指令、寫程式或提供世界知識。

**28.9M 為何放得進去？** 28.9M 是儲存參數量，不是同時載入 SRAM
的參數量，也不是「能力強 100 倍」。權重經 4-bit 量化後，upstream
reported 的匯出 artifact 是 14,912,332 bytes，可放進 15,597,568-byte
的 custom model partition。推論時，25M 參數的 Per-Layer Embeddings
（逐層嵌入）表保持記憶體映射於 Flash；輸出頭與工作記憶體使用 PSRAM；
SRAM 留給低延遲的運算狀態。細節與現行 firmware 的例外見
[架構解讀](docs/zh-TW/architecture.md)。

**目前能不能一鍵重現？** 不能。upstream 沒有提交展示用的
`firmware/model/model.bin`，也沒有發布生成它所需的
`runs/ple-cleandeploy-s0.pt` checkpoint／訓練檢查點。下一個可執行的
host 路徑是先取得或自行訓練相容 checkpoint，再執行：

```bash
cd src
uv run python export.py
cd ..
cc -O3 -o /tmp/esp32-llm-verify firmware/host_verify/verify.c -lm
/tmp/esp32-llm-verify firmware/model/model.bin firmware/model/golden.txt
```

以上命令來自 upstream
[`firmware/esp32_llm/README.md`](https://github.com/slvDev/esp32-ai/blob/74744182329f08d7a1badc97e47576ef527532a0/firmware/esp32_llm/README.md)；
在 checkpoint 缺失時，第一個 export command 便會阻塞。

## 證據狀態

| 項目 | 狀態 | 意義 |
|---|---|---|
| R0 Source audited | **本地驗證：PASS** | 已核對 commit、LICENSE、文件、分割區與缺失 artifact |
| R1 Environment reproduced | **尚未驗證** | P1 未安裝完整 Python／Arduino toolchain |
| R2 Host verified | **尚未驗證：BLOCKED** | 缺少相容 checkpoint，無法生成 `model.bin` 後跑 `firmware/host_verify` |
| R3 Firmware compiled | **尚未驗證** | 未執行 Arduino 無裝置 build |
| R4 Device generated | **尚未驗證** | 未使用 ESP32-S3 N16R8 實機 |
| R5 Performance reproduced | **尚未驗證** | 尚無本地 throughput、記憶體或輸出品質 receipt |

- **upstream reported：** 約 9.5 tok/s 端到端吞吐量，9.72 tok/s
  純運算吞吐量；本倉庫尚未 locally reproduced。
- **upstream reported：** 28.9M 儲存參數量、14.9MB 4-bit model artifact。
- **本地驗證：** 只完成 R0 靜態來源核對；完整 receipt 見
  [重現狀態](docs/zh-TW/reproduction-status.md)。

## 中文文件

- [原始公告翻譯](docs/zh-TW/original-announcement.md)
- [記憶體階層、量化與 PLE 架構解讀](docs/zh-TW/architecture.md)
- [RESULTS 核心結果與限制導讀](docs/zh-TW/results-guide.md)
- [firmware build／flash 操作指南](docs/zh-TW/firmware-guide.md)
- [R0–R5 重現狀態與 receipt](docs/zh-TW/reproduction-status.md)
- [第三方聲稱與 upstream 邊界](docs/zh-TW/third-party-claims.md)
- [繁體中文術語表](docs/zh-TW/glossary.md)
- [翻譯政策與同步方式](TRANSLATION.md)

## 來源與授權

- upstream repository：[`slvDev/esp32-ai`](https://github.com/slvDev/esp32-ai)
- inspected commit：[`74744182`](https://github.com/slvDev/esp32-ai/tree/74744182329f08d7a1badc97e47576ef527532a0)
- 原始作者：[Viacheslav Sierbov（slvDev）](https://x.com/slvDev)
- 原始頁面：[`README.md` — Running a 28.9M parameter LLM on an $8 microcontroller](https://github.com/slvDev/esp32-ai/blob/74744182329f08d7a1badc97e47576ef527532a0/README.md)
- 授權：[MIT License](LICENSE)
