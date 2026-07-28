# ESP32-S3 on-chip inference 韌體指南

本頁是 upstream
[`firmware/esp32_llm/README.md`](https://github.com/slvDev/esp32-ai/blob/74744182329f08d7a1badc97e47576ef527532a0/firmware/esp32_llm/README.md)
的忠實繁體中文翻譯。CLI commands、paths、SHA、位址與參數值保持原樣。

## 原文翻譯：用途

此 sketch 在 ESP32-S3 N16R8 上執行 28.9M 儲存參數量的 PLE TinyLM。
模型位於 `0x110000` 的 custom `model` Flash partition；tied
embedding／output head 在開機時 staged 到 PSRAM。

## 原文翻譯：Build and verify

先匯出 group-128 ragged-int4 模型，並驗證 portable C runtime：

```bash
cd src
uv run python export.py
cd ..
cc -O3 -o /tmp/esp32-llm-verify firmware/host_verify/verify.c -lm
/tmp/esp32-llm-verify firmware/model/model.bin firmware/model/golden.txt
```

使用 Arduino ESP32 core 3.3.10 build device firmware：

```bash
arduino-cli compile \
  --fqbn 'esp32:esp32:esp32s3:UploadSpeed=921600,USBMode=hwcdc,CDCOnBoot=cdc,UploadMode=default,CPUFreq=240,FlashMode=qio,FlashSize=16M,PartitionScheme=custom,PSRAM=opi,DebugLevel=info' \
  --build-property compiler.optimization_flags=-O3 \
  --build-path /tmp/esp32-llm-build \
  firmware/esp32_llm
```

## 原文翻譯：Flash and run

若開發板列舉為不同 device name，請替換 port：

```bash
arduino-cli upload \
  -p /dev/cu.usbmodem2101 \
  --fqbn 'esp32:esp32:esp32s3:UploadSpeed=921600,USBMode=hwcdc,CDCOnBoot=cdc,UploadMode=default,CPUFreq=240,FlashMode=qio,FlashSize=16M,PartitionScheme=custom,PSRAM=opi,DebugLevel=info' \
  --input-dir /tmp/esp32-llm-build \
  firmware/esp32_llm

esptool.py --chip esp32s3 --port /dev/cu.usbmodem2101 --baud 921600 \
  write_flash 0x110000 firmware/model/model.bin

arduino-cli monitor -p /dev/cu.usbmodem2101 --config baudrate=115200
```

只有在重新 export 模型後，才需要再次 flash model payload。只改 firmware
時，不需要重寫 model partition。

量測所用模型的 SHA-256：

```text
21067f5d78113f6c64a8720b05ff7e5c774dab0276797a522f81a6797253d97c
```

目前 artifact 的預期 boot diagnostics：

```text
model: V=32768 D=96 L=6 H=4 F=66 P=128
head staged int8: 2.53 MB
PSRAM free after alloc: ~5100 KB
```

upstream reported：目前 runtime 每個 model step 是 102.9ms（純運算吞吐量
9.72 tok/s）；連接 serial 的執行約為 9.5 tok/s 端到端吞吐量。

upstream reported：on-device profile 是 57.6ms output head、25.6ms
attention、8.5ms PLE path、6.9ms FFN、4.4ms input。

upstream reported：output head 以 int8 與 int8 activations staged
（經過 host validation，validation perplexity delta 約 0），目前受
PSRAM bandwidth 限制。fp32 host golden 仍與 PyTorch 相符到 `1e-5`。

## 尚未驗證：目前 blocker

本倉庫沒有執行以上 build／flash 流程。pinned upstream commit 不包含：

- `runs/ple-cleandeploy-s0.pt`
- `firmware/model/model.bin`
- `firmware/model/golden.txt`
- `firmware/esp32_llm/vocab.h`

`src/export.py` 預設先讀取
`runs/ple-cleandeploy-s0.pt`；缺少 checkpoint 時，不能生成後續
`model.bin` 與 golden files。請勿下載來源不明的 binary，或把第三方
artifact 冒充成上述 SHA-256 的展示模型。

完整狀態見 [`reproduction-status.md`](reproduction-status.md)。

## 來源 receipt

- upstream repository：[`slvDev/esp32-ai`](https://github.com/slvDev/esp32-ai)
- inspected commit：[`74744182`](https://github.com/slvDev/esp32-ai/tree/74744182329f08d7a1badc97e47576ef527532a0)
- 原始作者：Viacheslav Sierbov（slvDev）
- 原始頁面：[`firmware/esp32_llm/README.md` — ESP32-S3 on-chip inference](https://github.com/slvDev/esp32-ai/blob/74744182329f08d7a1badc97e47576ef527532a0/firmware/esp32_llm/README.md)
- license：[MIT License](../../LICENSE)
