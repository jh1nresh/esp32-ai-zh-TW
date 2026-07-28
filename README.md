# 在 8 美元微控制器上執行 28.9M 儲存參數量 LLM

[English](README.en.md) · [完整 RESULTS 繁中翻譯](RESULTS.zh-TW.md) ·
[翻譯政策](TRANSLATION.md)

> 本倉庫是 slvDev/esp32-ai 的非官方繁體中文翻譯、技術解讀與重現紀錄。
> 原始專案作者為 Viacheslav Sierbov（slvDev），依 MIT License 使用。
> 如翻譯與英文原文有歧義，以 upstream 原文為準。
> 所有效能數字都必須標示為 upstream reported 或 locally reproduced。

翻譯基準：[`slvDev/esp32-ai`](https://github.com/slvDev/esp32-ai) commit
[`74744182329f08d7a1badc97e47576ef527532a0`](https://github.com/slvDev/esp32-ai/tree/74744182329f08d7a1badc97e47576ef527532a0)。

<p align="center">
  Open to Work &nbsp;·&nbsp;
  <a href="https://x.com/slvDev">𝕏 slvDev</a> &nbsp;·&nbsp;
  <a href="https://www.linkedin.com/in/slvdev/">LinkedIn</a>
</p>

![在 ESP32-S3 上執行的 28.9M 儲存參數量 LLM](media/esp32-ple-demo.gif)

## 原文翻譯

這是一個在 ESP32-S3 上生成文字的 28.9M 儲存參數量語言模型；這顆
微控制器約售 8 美元。模型直接在晶片上運行，不會把任何資料送到
server；upstream reported：它以約 9 tok/s 的速度，把每個詞寫到小型
螢幕上。先前有人在同類晶片上運行的語言模型只有 260K parameters，
所以本模型保存的參數量約為前者 100 倍。它能夠放得進去，是因為模型
大部分內容使用 Google Gemma 模型的 Per-Layer Embeddings
（逐層嵌入）概念，存放在 Flash 而不是 RAM。

## 數字

以下數值全部為 upstream reported，尚未 locally reproduced。

| | |
|---|---|
| 儲存參數量 | 28.9M（其中 25M 位於 Flash lookup table） |
| 晶片 | ESP32-S3，約 8 美元，512KB SRAM、8MB PSRAM、16MB Flash |
| 速度 | upstream reported：約 9.5 tok/s 端到端吞吐量（9.7 tok/s 純運算吞吐量） |
| 連線 | 無；所有運算都在裝置上完成 |
| 模型大小 | 14.9MB，4-bit |

## 難點是什麼，又如何放得進去

微控制器的快速記憶體非常少。ESP32-S3 只有 512KB SRAM。一般情況下，
整個模型都必須能從這裡取得，因此模型規模會受到嚴格限制；這也是先前
在同類晶片上運行的模型只有 260K parameters 的原因。

解法是不再把整個模型放進快速記憶體。語言模型的大量參數位於 embedding
table；模型會查表，而不是每次對整張表做運算。因此可以把 25M-parameter
table 留在較慢的 Flash，每個 token 只取用它需要的少數 rows，約 450
bytes；真正執行運算的小型部分則使用快速記憶體。大型 table 幾乎不增加
執行成本，因為模型永遠不會載入其中大多數資料；它留在 Flash，推論時
只取樣少量內容。

這就是 Google Gemma 3n 與 Gemma 4 使用的 Per-Layer Embeddings。此處把
它套用於微控制器的記憶體配置，而不是手機或 GPU。依 upstream 作者所知，
過去沒有人在如此小的晶片上嘗試這個方法。

```text
SRAM  （快、極小）  每個 token 都會使用的「思考」核心
PSRAM （中等）      輸出頭與工作記憶體
FLASH （大、較慢）  25M-parameter table；每個 token 約讀 6 rows（約 450 B）
```

更精確的現行 firmware 記憶體配置與量化計算，見
[架構解讀](docs/zh-TW/architecture.md)。

## 它能做什麼，不能做什麼

模型使用 TinyStories 訓練，因此會撰寫簡短、簡單，而且大致連貫的故事。
它不會可靠地回答問題、遵循指令、寫程式或知道事實。這個限制來自模型中
負責 reasoning 的小型部分，而記憶體技巧不會改變它。這項工作的重點是
把大型儲存模型放進小型晶片的架構，不是 28.9M 儲存參數量模型能說出
什麼內容。

這也不是中文模型、語音助理、intent classifier、BLE／BTHome／Home
Assistant 節點或 ESP32 swarm。相關社群延伸與 upstream 的界線見
[第三方聲稱](docs/zh-TW/third-party-claims.md)。

## 自己執行

firmware、接線與 flashing 步驟見
[`docs/zh-TW/firmware-guide.md`](docs/zh-TW/firmware-guide.md)；英文原文
是 [`firmware/esp32_llm/README.md`](firmware/esp32_llm/README.md)。
training、ablation 與 quantization code 位於 `src/` 和 `experiments/`。
完整方法、ablations 與 on-chip measurements 已完整翻譯至
[`RESULTS.zh-TW.md`](RESULTS.zh-TW.md)，英文原文保留在
[`RESULTS.md`](RESULTS.md)。

目前不能一鍵重現：upstream 沒有提交展示用的
`firmware/model/model.bin`，也沒有發布生成它所需的
`runs/ple-cleandeploy-s0.pt` checkpoint。取得或自行訓練相容 checkpoint
後，下一個 host 驗證路徑是：

```bash
cd src
uv run python export.py
cd ..
cc -O3 -o /tmp/esp32-llm-verify firmware/host_verify/verify.c -lm
/tmp/esp32-llm-verify firmware/model/model.bin firmware/model/golden.txt
```

完整阻塞點與 command receipt 見
[R0–R5 重現狀態](docs/zh-TW/reproduction-status.md)。

## 致謝

TinyStories 是本模型的訓練資料集：它由簡短的 synthetic stories 組成，
內容簡單到小型模型仍能學會連貫寫作（Ronen Eldan 與 Yuanzhi Li，
Microsoft Research，[arXiv:2305.07759](https://arxiv.org/abs/2305.07759)）。
另一半是 Google Gemma 模型的 Per-Layer Embeddings 設計，使大型模型
能放進小型晶片。

Andrej Karpathy 的 [`llama2.c`](https://github.com/karpathy/llama2.c)
讓包括 upstream 作者在內的許多人相信：可以訓練小型語言模型，並以
plain C 執行。這個專案也從該脈絡發展而來。

## 實際研究過程

upstream 作者刻意保留了不整齊的 commit history，其中包含作者發現的
parameter accounting bug；該 bug 曾使早期數字被高估，修正後才得到
目前結果。commit history 與 `RESULTS.md` 記錄了數字如何變化，以及
變化原因。

## 本倉庫驗證狀態

| Level | 狀態 |
|---|---|
| R0 Source audited | **本地驗證：PASS** |
| R1 Environment reproduced | **尚未驗證** |
| R2 Host verified | **尚未驗證：BLOCKED**，缺少 checkpoint／`model.bin` |
| R3 Firmware compiled | **尚未驗證** |
| R4 Device generated | **尚未驗證** |
| R5 Performance reproduced | **尚未驗證** |

## 繁中技術文件

- [原始公告翻譯](docs/zh-TW/original-announcement.md)
- [記憶體階層、量化與 PLE 架構解讀](docs/zh-TW/architecture.md)
- [完整 RESULTS 翻譯](RESULTS.zh-TW.md)
- [RESULTS 快速導讀](docs/zh-TW/results-guide.md)
- [firmware build／flash 完整翻譯](docs/zh-TW/firmware-guide.md)
- [R0–R5 重現狀態與 receipt](docs/zh-TW/reproduction-status.md)
- [第三方聲稱與 upstream 邊界](docs/zh-TW/third-party-claims.md)
- [繁體中文術語表](docs/zh-TW/glossary.md)
- [翻譯政策與同步方式](TRANSLATION.md)

## 來源與授權

- upstream repository：[`slvDev/esp32-ai`](https://github.com/slvDev/esp32-ai)
- inspected commit：[`74744182`](https://github.com/slvDev/esp32-ai/tree/74744182329f08d7a1badc97e47576ef527532a0)
- 原始作者：[Viacheslav Sierbov（slvDev）](https://x.com/slvDev)
- 英文原始頁面：[`README.en.md`](README.en.md)
- 授權：[MIT License](LICENSE)
