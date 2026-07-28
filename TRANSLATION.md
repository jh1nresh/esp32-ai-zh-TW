# Translation contract

本文件定義 `esp32-ai` 非官方完整繁體中文文件的來源、標籤與同步規則。

## Source baseline

- upstream：[`slvDev/esp32-ai`](https://github.com/slvDev/esp32-ai)
- inspected commit：[`74744182329f08d7a1badc97e47576ef527532a0`](https://github.com/slvDev/esp32-ai/tree/74744182329f08d7a1badc97e47576ef527532a0)
- original author：Viacheslav Sierbov（slvDev）
- license：[MIT License](LICENSE)
- language：`zh-TW`（繁體中文）
- last source sync：2026-07-28，基準 commit 如上

此翻譯使用 AI 協助起草，並逐項對照上述 commit 的 `README.md`、
`RESULTS.md`、`firmware/esp32_llm/README.md`、原始 X 公告與 repository
內容。它不是 upstream 作者提供或認可的官方翻譯。

## 文件對照

| upstream source | 繁中版本 | 狀態 |
|---|---|---|
| `README.md` | [`README.md`](README.md) | 完整翻譯；GitHub 預設入口 |
| `README.md` | [`README.en.md`](README.en.md) | pinned 英文原文，byte-for-byte 保留 |
| `RESULTS.md` | [`RESULTS.zh-TW.md`](RESULTS.zh-TW.md) | 完整翻譯 |
| `firmware/esp32_llm/README.md` | [`docs/zh-TW/firmware-guide.md`](docs/zh-TW/firmware-guide.md) | 完整翻譯；所有 code blocks 原樣保留 |

[`README.zh-TW.md`](README.zh-TW.md) 只作為既有連結的相容入口，完整內容
以 root [`README.md`](README.md) 為單一中文首頁。

## Evidence labels

每個實質段落使用下列其中一種證據角色；表格、清單或同一小節中的短句
可共用緊鄰的標籤：

- `原文翻譯`：忠實傳達指定 upstream 來源，不擴大結論。
- `譯註`：用繁體中文解釋術語、計算或歧義。
- `本地驗證`：附日期、環境、完整命令、exit code 與觀察輸出。
- `第三方聲稱`：只代表被引用的第三方，不代表 upstream 實作。
- `尚未驗證`：缺少 artifact、hardware 或 command output，不能升級 receipt。

效能數字另外使用英文 evidence marker `upstream reported` 或
`locally reproduced`，讓文件檢查可以機械判斷。沒有 command output
不得使用 `locally reproduced`。

## 不翻譯的內容

以下內容保持原樣：

- CLI command、API／symbol／function 名稱；
- JSON keys、environment variables、paths、filenames；
- 型號、commit SHA、位址、參數值；
- upstream MIT License 原文。

固定術語見 [`docs/zh-TW/glossary.md`](docs/zh-TW/glossary.md)。`stored
parameters` 一律譯為「儲存參數量」，不得改寫為「模型能力」；
`~100x parameters` 不得改寫為「強 100 倍」。

## Upstream precedence and sync

若翻譯與英文來源有歧義，以 pinned upstream source 為準。同步時：

1. fetch upstream，但不要直接覆寫中文文件；
2. 比較目前基準 commit 與新 commit 的 upstream `README.md`、
   `RESULTS.md`、`firmware/esp32_llm/README.md` 及 LICENSE；
3. 先更新 byte-for-byte 英文鏡像 `README.en.md`，再逐段更新
   `README.md`、`RESULTS.zh-TW.md`、firmware 翻譯、來源連結與
   evidence label；
4. 更新本文件的 commit 與 `last source sync`；
5. 執行 `python3 scripts/check_docs.py` 與 `git diff --check`；
6. 若效能或能力結論改變，保留舊 receipt，新增有日期的新 receipt。

## Attribution receipt

- repository：[`slvDev/esp32-ai`](https://github.com/slvDev/esp32-ai)
- commit：[`74744182`](https://github.com/slvDev/esp32-ai/tree/74744182329f08d7a1badc97e47576ef527532a0)
- author：Viacheslav Sierbov（slvDev）
- license：[MIT License](LICENSE)
- original source：[`README.md`](https://github.com/slvDev/esp32-ai/blob/74744182329f08d7a1badc97e47576ef527532a0/README.md)
