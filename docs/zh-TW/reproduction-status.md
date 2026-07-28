# R0–R5 重現狀態

狀態只由 command output 升級。upstream 的文字、影片或數字可以支持
source audit，但不能代替本地 host、firmware 或 device receipt。

## 狀態總覽

| Level | Definition | Current status |
|---|---|---|
| R0 Source audited | 核對 repo、commit、license、文件與缺失 artifact | **PASS — 本地驗證 2026-07-28** |
| R1 Environment reproduced | Python／uv／Arduino toolchain 可安裝並記錄版本 | **BLOCKED／尚未驗證** |
| R2 Host verified | 生成 model artifact 並通過 `firmware/host_verify` | **BLOCKED／尚未驗證** |
| R3 Firmware compiled | ESP32-S3 N16R8 firmware 無裝置 build 通過 | **NOT RUN／尚未驗證** |
| R4 Device generated | 實機燒錄並生成可讀 TinyStories 文字 | **NOT RUN／尚未驗證** |
| R5 Performance reproduced | 實測 throughput、記憶體與輸出品質 | **NOT RUN／尚未驗證** |

## R0 receipt — Source audited

```text
Date: 2026-07-28
Upstream commit: 74744182329f08d7a1badc97e47576ef527532a0
Host OS/tool versions:
  Darwin 25.6.0 arm64
  git version 2.51.0
  Python 3.11.4
  uv 0.11.8 (0e961dd9a 2026-04-27 aarch64-apple-darwin)
  arduino-cli: not installed / no version output
Hardware: N/A — static source audit only
Exact command:
  git ls-remote https://github.com/slvDev/esp32-ai.git HEAD refs/heads/main
  git rev-parse HEAD
  git archive 74744182329f08d7a1badc97e47576ef527532a0 | shasum -a 256
  test -f firmware/model/model.bin
  test -f runs/ple-cleandeploy-s0.pt
Exit code:
  git ls-remote: 0
  git rev-parse: 0
  git archive | shasum: 0
  model.bin presence check: 1
  checkpoint presence check: 1
Observed output:
  remote HEAD = 74744182329f08d7a1badc97e47576ef527532a0
  local HEAD  = 74744182329f08d7a1badc97e47576ef527532a0
  firmware/model/model.bin is absent
  runs/ple-cleandeploy-s0.pt is absent
Artifact SHA-256:
  ac14df6b60ebf53d3141d1dc3423357922cc76fc5b7a6dfaab3a1837d586bfd4
  (SHA-256 of `git archive` for the pinned commit)
Pass / fail / blocked: PASS (R0 only)
Residual difference from upstream:
  No source difference at audit start. R1-R5 have not been reproduced.
```

R0 另核對：

- `LICENSE` 是 MIT License，copyright 為 Viacheslav Sierbov；
- `firmware/esp32_llm/partitions.csv` 的 model partition 位址是 `0x110000`；
- `.gitignore` 排除 `runs/`、`firmware/model/model.bin`、golden files 與
  `firmware/esp32_llm/vocab.h`；
- upstream Issue #5 正在請求展示用 weights／checkpoint。

## R1 receipt — Environment reproduced

```text
Date: 2026-07-28
Upstream commit: 74744182329f08d7a1badc97e47576ef527532a0
Host OS/tool versions: Python 3.11.4; uv 0.11.8; arduino-cli unavailable
Hardware: N/A
Exact command: not run
Exit code: N/A
Observed output: pyproject.toml requires Python >=3.12; complete environment not installed
Artifact SHA-256: N/A
Pass / fail / blocked: BLOCKED / NOT RUN
Residual difference from upstream: Python requirement and Arduino ESP32 core 3.3.10 not verified
```

## R2 receipt — Host verified

```text
Date: 2026-07-28
Upstream commit: 74744182329f08d7a1badc97e47576ef527532a0
Host OS/tool versions: see R0
Hardware: N/A
Exact command: not run
Exit code: N/A
Observed output: default export input runs/ple-cleandeploy-s0.pt is absent
Artifact SHA-256: N/A; upstream reported model SHA-256 is not a local artifact
Pass / fail / blocked: BLOCKED
Residual difference from upstream: cannot generate model.bin/golden.txt or run firmware/host_verify
```

## R3–R5 receipts

```text
Date: 2026-07-28
Upstream commit: 74744182329f08d7a1badc97e47576ef527532a0
Host OS/tool versions: see R0
Hardware: none used
Exact command: not run
Exit code: N/A
Observed output: no firmware build, flash, serial generation, or performance measurement
Artifact SHA-256: N/A
Pass / fail / blocked: NOT RUN
Residual difference from upstream: all device and performance claims remain upstream reported
```

## 下一個可升級步驟

1. R1：在隔離環境安裝 Python 3.12、`uv` dependencies、`arduino-cli`
   與 Arduino ESP32 core 3.3.10，記錄版本與 exit codes。
2. R2：取得可追溯 checkpoint 或依 upstream 設定重新訓練，再執行
   `src/export.py` 與 `firmware/host_verify`；記錄輸出 artifact SHA-256。
3. R3：只有 R2 artifact 成功後，才進行無裝置 firmware compile。
4. R4–R5：需要 ESP32-S3 N16R8、燒錄 receipt、serial output 與量測方法。

## 來源 receipt

- upstream repository：[`slvDev/esp32-ai`](https://github.com/slvDev/esp32-ai)
- inspected commit：[`74744182`](https://github.com/slvDev/esp32-ai/tree/74744182329f08d7a1badc97e47576ef527532a0)
- 原始作者：Viacheslav Sierbov（slvDev）
- 原始頁面：[`README.md` — Running it yourself](https://github.com/slvDev/esp32-ai/blob/74744182329f08d7a1badc97e47576ef527532a0/README.md#running-it-yourself)
- license：[MIT License](../../LICENSE)
