# H5-CAM 探针样例 v1.0 / H5-CAM Probe Sample v1.0

本仓库是 H5-CAM 探针样例的发布冻结。发布标签 **v1.0** 等于内容版本 **v1.9**（`docs/h5/drill-cam-v1.9.html`，发布别名 `docs/h5/drill-cam-v1.0.html`）。

This repository is the H5-CAM probe sample freeze. Release tag **v1.0** is content version **v1.9** (`docs/h5/drill-cam-v1.9.html`, published alias `docs/h5/drill-cam-v1.0.html`).

## 运行 / Run

在仓库根目录执行：

```bash
cd docs/h5 && python3 -m http.server 8765
```

然后打开 [http://127.0.0.1:8765/drill-cam-v1.0.html](http://127.0.0.1:8765/drill-cam-v1.0.html)。

From the repository root, run the command above, then open `http://127.0.0.1:8765/drill-cam-v1.0.html`.

## 计时锁定 / Timing lock

- 总时长 60 秒 / time limit **60s**
- 保持 3 秒 / hold **3s**
- 冷却 2 秒 / cooldown **2s**
- 双路径 / **dual-path**：瞬时判定通过，或维持满 3 秒，先到先计。Instant pass or a full 3s hold, whichever comes first.

## 标签含义 / Tag meaning

- `v1.0` 是附注发布标签，标在这次样例冻结提交上。检出方式：`git fetch --tags && git checkout v1.0`。
- 内容版本是 v1.9。`drill-cam-v1.0.html` 与 `drill-cam-v1.9.html` 是同一份冻结页面。
- `v1.0` is the annotated release tag on this sample-freeze commit. Check it out with `git fetch --tags && git checkout v1.0`.
- The content version is v1.9. `drill-cam-v1.0.html` and `drill-cam-v1.9.html` are the same frozen page.
