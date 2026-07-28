# 實驗結果

[English source](RESULTS.md) · [繁中 README](README.md)

> `原文翻譯`：本頁完整對應 pinned upstream `RESULTS.md` 的所有章節。
> 所有實驗與效能數字均為 upstream reported，尚未 locally reproduced。

以下所有數字使用一致的三層 parameter accounting（core 不包含 head；
見 `src/budget.py`）。較早混用 accounting 的 runs 已封存至
`runs/_archive_old_accounting/`，不應引用。

upstream reported：**狀態（2026-07-21）：已完成端到端驗證。** PLE
在 2 個 seeds 中勝過 baseline；經 4-bit PTQ 後仍保有優勢（2 個
seeds）；on-chip bandwidth 證實 Flash table 的成本近乎可忽略；完整
28.9M 儲存參數量模型已在 ESP32-S3 N16R8 上生成連貫文字。C runtime
以約 **9.5 tok/s 端到端吞吐量**生成文字（viewer 實際看到的速度，包含
serial output），相當於 102.9ms/model step，或 9.72 tok/s 純運算吞吐量。
runtime 使用 int8-staged output head 與 int8 activations；upstream
已在 host 驗證，validation perplexity delta 約為 0。公開引用應以
端到端數字為主。

## Headline：可部署設定

Vocab 32768；各 arms 的 core 都控制在約 559K parameters（4-bit 時
273KB，小到能符合 ESP32-S3 512KB internal SRAM 的設計限制；polished
firmware 實際讓 core 保持 Flash-mapped XIP，因為量測顯示速度足夠，見
on-chip 章節）；25M-parameter PLE table（12MB Flash）；
`d_model=96`、6 layers、`ple_dim=128`。每個 arm 使用 2 個 seeds。

| arm | core | total | ppl | 相對 baseline |
|---|---:|---:|---:|---:|
| `baseline` | 559K | 3.7M | 12.58 | — |
| **`ple`** | 558K | **28.9M** | **11.41** | **+0.098 nats／9.3% ppl** |
| `fatembed` | 559K | 28.9M | 11.94 | +0.052 nats |

- upstream reported：**PLE 在相同 core、能放入 SRAM 的 baseline 上改善
  0.098 nats（2 seeds，±0.006），約為 seed noise 的 16 倍。**
  ppl 從 12.58 降至 11.41。
- upstream reported：**逐層注入比底部注入改善 0.046 nats**（`ple`
  對 `fatembed`，兩者皆為 2 seeds）。在實際 vocab 規模下，注入位置
  帶來的價值約為只在底部增加 parameters 的 2 倍。
- 比較背景（先前獨立工作，與本 codebase 無關）：DaveBben 的
  `esp32-llm` 在 ESP32-S3 上執行 260K parameters。本模型的儲存參數量
  約為 110 倍，fast-memory 預算更緊，而且額外 parameters 位於 Flash
  的 per-token-sparse table。

**「28.9M parameters」代表與不代表什麼。** 它是 28.9M
**儲存參數量**：559K dense core（SRAM 預算）、3.1M output head
（sequentially streamed）與 25M lookup table（Flash，每個 token
取用一個 row）。它仍然是 TinyStories-domain model；改善的是 coherence
與 consistency，不是新增能力。應引用為「透過 memory-hierarchy split
常駐的 parameters」，不得寫成能力倍數。

## Vocab 為何重要，以及 small-vocab 數字為何較小

相同架構在 vocab 4096、core 約 1.5M 且 matched、2 seeds 時：

| arm | ppl | 相對 baseline |
|---|---:|---:|
| `baseline` | 8.21 | — |
| `ple_notable` | 8.35 | **-0.017（較差）** |
| `fatembed` | 8.26 | -0.006（近乎無差異） |
| `ple` | 8.00 | +0.025 |
| `bigcore`（2x core） | 6.93 | +0.170 |

upstream reported：vocab 4096 時，PLE 優勢只有 +0.025 nats；vocab 32768
時則為 +0.098，擴大 **4 倍**。這正是 memory-tiering thesis 生效：
大型 vocabulary 會使 table 變得既大又便宜（更多 rows，但每個 token
只稀疏查詢），也正是 PLE 的設計使用情境。部署設定位於有利區間；
small-vocab ablation 是 control，不是產品設定。

## Controls 證明了什麼

- **真正產生效果的是 table，而不是周邊結構。** `ple_notable` 具備
  PLE 的所有 per-layer adapters 與 projection，但沒有 lookup table；
  vocab 4096 時反而比 baseline 差 -0.017。若沒有 table 輸入資料，
  plumbing 只會花掉 core parameters。table 的 isolated contribution
  （`ple` - `ple_notable`）為 +0.043。因此 Flash-resident table 是
  gain 的全部來源，符合 ESP32 premise 所需。
- **Row width 會飽和，vocab rows 在測試範圍內不會。** 修正後的 sweep
  （`runs/*fix-d*`，固定 FFN、vocab 4096）顯示：擴大 `ple_dim`
  （row width）時，isolated table benefit 在約 6M table 附近達峰：
  +0.045（d64）→ +0.094（d256）→ +0.087（d512）。部署設定則以另一種
  方式擴大 table：使用 32k vocab 增加 rows；該設定下 25M table 仍有
  明確效益（+0.098）。在已測範圍內，擴寬 rows 會 plateau，增加 rows
  不會。
- **PLE 不是免費 capacity。** `bigcore`（2x dense core）在 vocab 4096
  得到 +0.170。PLE 在 vocab 4096 只取回約 15%，vocab 32768 時更多。
  在 desktop 上可以直接擴大 core；ESP32 的 core 受固定 silicon 限制，
  而 Flash 相對充足，這正是整個方法的前提。

## Hardware：N16R8 bandwidth 實測（2026-07-21）

upstream 在真實 ESP32-S3 上以 `firmware/bandwidth_bench` 量測，使用
Xtensa cycle counter 做 cycle-accurate timing。這些實測把估計 tok/s
轉成硬體數據，也是整個方法所依賴的基礎。

| measurement | upstream reported value |
|---|---:|
| PSRAM sequential read | upstream reported：60.7 MB/s |
| internal SRAM sequential read | upstream reported：240 MB/s |
| Flash random-read，512B row | upstream reported：20.3 us |
| **每個 token 的 TABLE cost**（6 random rows） | **upstream reported：約 0.12 ms** |
| **每個 token 的 HEAD cost**（1.5MB PSRAM scan） | **upstream reported：約 17.3 ms** |
| **bandwidth-only tok/s ceiling** | **upstream reported：約 58 tok/s** |

upstream reported：**核心假設已在 silicon 上確認。** 在 isolated
bandwidth benchmark 中，25M-parameter Flash table 只佔每 token memory
time 約 0.7%，幾乎可忽略，符合設計。output HEAD（baseline 同樣需要）
主導 memory traffic。這尚不是完整的 PLE-vs-baseline 端到端速度比較；
引用 0.7% 時必須限定為 table 的 synthetic bandwidth share，不得寫成
total inference overhead。

upstream reported：58 tok/s 只是 bandwidth-only ceiling，不是觀察到的 inference
throughput。第一個完整 scalar port 顯示，int4 unpacking 與數百萬次
scalar float operations 早在 raw bandwidth 前就成為瓶頸。20us random
read latency 確實存在，不是 0；在目前 `ple_dim`／layer count 下仍可忽略，
但 table 更寬時會增加。

## On-chip generation：完整模型運行（2026-07-21）

upstream reported：匯出的模型是 14,912,332 bytes，可放入
15,597,568-byte custom Flash partition，剩餘 685,236 bytes。619KB
application 位於另一個 1MB partition。portable C runtime 在所有
32,768 logits 上與 exported PyTorch golden 相符
（`max abs diff = 0.00001`），之後才把同一份 code 編譯到裝置。

在 ESP32-S3 上，1.64MB tied embedding／output head 於開機時複製到
PSRAM；25M-parameter PLE table 保持 memory-mapped 於 Flash；scratch
與 KV cache 位於 PSRAM。完成所有 allocations 後，仍有 5,228KB PSRAM。
從 `Once upon a time` 開始做 greedy generation，可以產生連貫的
TinyStories text。upstream 捕捉的一段 on-device continuation，其繁中
意譯如下；這不是模型直接生成的中文：

> 很久很久以前，有個名叫 Lily 的小女孩。她喜歡在陽光下到戶外玩耍。
> 有一天，她看到一棵大樹，樹上有個洞。她很好奇，想看看裡面有什麼。

| implementation | 200-token result | model-step time |
|---|---:|---:|
| first correct portable port | upstream reported：0.57 tok/s 端到端 | upstream reported：1,757.2 ms |
| PSRAM head + scalar cleanup | upstream reported：4.61–4.77 tok/s 端到端 | upstream reported：193.9 ms |
| exact dot/RoPE/attention cleanup | — | upstream reported：172.9 ms |
| dual-core exact head | upstream reported：5.67–6.22 tok/s 端到端 | upstream reported：139.4 ms |
| **int8-staged head + int8 activations** | **upstream reported：約 9.5 tok/s 端到端** | **upstream reported：102.9 ms** |

upstream reported：int8 head 是目前 runtime：**9.72 tok/s 純運算吞吐量**
（102.9 ms/step），比 exact fp32 dual-core head 再快 1.35 倍。output
head 在 boot 時一次性以 int8 staged 到 PSRAM（int4 nibbles 只 unpack
一次），activations 則每個 token 量化為 int8，因此每個 output row
只需 plain int8×int8 → int32 dot，不用每個 token 再 unpack。upstream
先以 host validation perplexity 驗證 int8-activation change
（delta 約 0；見 `firmware/host_verify/ppl.c`），on-chip text 仍保持
coherent。scalar fp32 head（139.4ms）保留為 exact baseline；fp32 host
golden 仍與 PyTorch 相符至 `1e-5`。

upstream reported：int8 head 後的 profile（ms/token，dual-core wall）：
head 57.6、attention 25.6、PLE 8.5、FFN 6.9、input 4.4。head 現在受
**PSRAM bandwidth，而不是 compute** 限制：每個 token 讀取 2.43MB
int8 weights；以 60.7 MB/s 計算，floor 約 40ms，所以 compute 只佔約
17ms。S3 vector-SIMD 即使實作，也只能減少那 17ms，整體進一步改善上限
約 15%。下一個較大槓桿是減少 bytes-read（int4 head + SIMD unpack），
或使用更小／factorised output head（model change），而不是繼續強化
vectorisation。

upstream reported：較早的 fp32 exact optimizations（139.4ms baseline）包含：把 head staged
到 PSRAM；每個 fp16 group scale 只轉換一次；每 byte unpack 兩個 int4
values；在 dot product 後套用 group scale；以 `-O3` 編譯；跳過 7,415
個不可到達的 padded vocabulary rows；每 token 只計算一次 RoPE values；
cache attention scores；並把獨立 output rows 分配到兩個 LX7 cores。

upstream reported：較早 exact fp32-head path（139.4ms/step，已被 int8 head 取代）的
historical profile 如下。數值為 200 generated tokens 的平均 wall-time
share；head 在兩個 cores 上運行，所以其 compute share（約 80%）高於
wall share：

| stage | upstream reported ms/token（wall） | wall share |
|---|---:|---:|
| output head（dual-core） | upstream reported：93.2 ms/token | 66.9% |
| attention | upstream reported：26.4 ms/token | 18.9% |
| PLE input + per-layer path | upstream reported：12.9 ms/token | 9.3% |
| FFN | upstream reported：6.9 ms/token | 4.9% |

upstream reported：把其餘 0.29MB quantized core 明確 staged 到 PSRAM、
norms 放入 internal RAM，只省下 2.0ms/token（1.4%），卻增加 allocation
complexity，因此 polished runtime 移除了該實驗。

upstream reported：仍有範圍有限的 exact work：parallel attention、precomputed RoPE
frequencies 與 one-group-specialized head loop；但 profile 顯示整個
attention opportunity 上限是 26.4ms，其他項目只有 low single-digit
milliseconds。upstream 刻意延後這些工作，而沒有把它們呈現成另一個
大型 scalar speedup。

upstream reported：實測 throughput 遠低於 58 tok/s bandwidth ceiling，
也推翻早期對 naive scalar kernel 的 20–40 tok/s compute estimate。
儘管如此，它與先前獨立 260K-parameter ESP32 專案仍處於相近實用速度，
同時保存約 110 倍儲存參數量。int8 activations 已出貨，而且 head 已受
PSRAM bandwidth 限制；下一個大型 speed step 是減少讀取 bytes
（int4-in-PSRAM head + SIMD unpack），或 factorized／smaller output
head，而不是更多 scalar cleanup，也不是 PLE table bandwidth 問題。

## 4-bit quantization：優勢仍保留（2026-07-21）

Group-wise symmetric int4 PTQ（group 64），即準備寫入 Flash 的
GGUF-Q4-style format（`src/quantize.py`）。所有大型 weights 都經過
quantization，包括 25M table。使用 2 seeds、vocab 32768 deploy models。

| arm | fp32 → 4-bit degradation |
|---|---|
| `baseline` | +0.079／+0.088 nats |
| `ple` | +0.055／+0.061 nats |
| `fatembed` | +0.046／+0.050 nats |

upstream reported：PLE 對 baseline 的優勢從 fp32 +0.101／+0.095，變成
4-bit +0.125／+0.121，亦即**完整保留 124–128%**。必須仔細解讀：
所有 arms 在 4-bit 下都退化（ppl 約 +1）；PLE 退化較少，因為具有
per-group scales 的大型 redundant lookup table，本質上比每個 weight
都重要的小型 dense model 更能承受 quantization。因此用掉 Flash budget
的部分，同時也是最能承受 4-bit 的部分。headline **不需要 QAT**。

最終 Flash artifact 使用更緊密的 group-128 format、ragged rows 與
fp16 scales，以放入 16MB Flash。upstream 也在兩個 seeds 上驗證實際
storage scheme：

| arm | fp32 → shipping-format degradation |
|---|---|
| `baseline` | +0.089／+0.109 nats |
| `ple` | +0.063／+0.089 nats |
| `fatembed` | +0.056／+0.061 nats |

upstream reported：PLE edge 在 fp32 是 +0.101／+0.095 nats，在 shipping
format 是 +0.127／+0.115，亦即保留 **126%／121%**。因此實際寫入
開發板的 bytes 與 group-64 headline PTQ check 得到相同 two-seed 結論。

## 其餘限制

- **仍未使用 ESP32-S3 SIMD instructions。** shipping runtime
  upstream reported：約 9.5 tok/s 端到端吞吐量；它會把 activations
  量化成 int8，已在 host 驗證，但 dot products 仍是 scalar。head 受
  PSRAM bandwidth 限制（57.6ms 中約有 40ms read floor），所以 SIMD
  單獨最多改善約 15%；真正的槓桿是減少 bytes read（int4 head + SIMD
  unpack）或使用更小的 head。58 tok/s 仍只是 bandwidth ceiling。
- **Domain 是 TinyStories。** world knowledge、arithmetic 與 multi-step
  reasoning 仍不存在；這個 ceiling 由 dense core 決定，不會被 table
  改變。
- **Provenance。** 這是獨立工作。實際 dependencies 是 TinyStories
  dataset（Eldan & Li，Microsoft Research，arXiv:2305.07759）與 Google
  公開的 Gemma Per-Layer Embeddings design（根據 `transformers` Gemma
  implementation 與 Google documentation 重現）。程式碼、模型、
  checkpoint 與方法皆非衍生自 `llama2.c`（Karpathy）或 DaveBben 的
  `esp32-llm`；兩者只作為 tiny-LM／microcontroller space 的獨立先前工作
  與比較背景。此處的新穎性主張很窄：把 Gemma-style Per-Layer
  Embeddings 套用到 microcontroller SRAM／Flash hierarchy，使儲存模型
  可大於 fast memory 容量。

## 下一步

1. 加入 interactive serial prompting／tokenization，再進行 dialogue
   fine-tuning，達到 simple-conversation milestone。
2. 錄製 on-chip text-generation demo，發布 measured result。
3. upstream reported：把 ESP32-S3 SIMD／int8 head 當成獨立實驗，將品質與速度和 exact
   139.4ms/token baseline 比較。

## 來源 receipt

- upstream repository：[`slvDev/esp32-ai`](https://github.com/slvDev/esp32-ai)
- inspected commit：[`74744182`](https://github.com/slvDev/esp32-ai/tree/74744182329f08d7a1badc97e47576ef527532a0)
- 原始作者：Viacheslav Sierbov（slvDev）
- 英文原始頁面：[`RESULTS.md`](RESULTS.md)
- license：[MIT License](LICENSE)
