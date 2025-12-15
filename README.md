# 视觉算法自动处理服务器

**概述**
- 前端页面自动轮询最新图片与结果，展示识别分拣结果。
- 后端提供上传接口、结果查询接口、静态文件服务与可选的“处理器插件”机制。
- 算法脚本 `model/getShapeVideo1.py` 由后端调用，生成 `result/<basename>_result.txt`。

**目录结构**
- `html/html_files/index.html`：前端页面（自动轮询最新图片与结果）。
- `html/css_files/sunny.css`：主题样式（页面使用此样式）。
- `python/app.py`：Flask 服务（端口 `5401`）。
- `python/processors/`：处理器插件（示例为占位处理器）。
- `uploads/`：上传与处理后图片的保存目录。
- `result/`：文本结果输出目录。
- `model/getShapeVideo1.py`：算法脚本（由后端调用）。

**环境准备**
- Python 3.8+
- 依赖包：`flask`, `Pillow`（基础必需）；`watchdog`、`opencv-python`、`torch` 视算法需要可选安装。

**快速开始**
- 启动后端服务：在项目根目录执行：
  - `python python/app.py`
  - 访问 `http://localhost:5401/`

- 上传图片（由主机/脚本推送，页面端上传已禁用）：
  - 接口：`POST /upload`，`form-data` 字段名 `file`
  - 保存位置：`uploads/`，返回文件名与访问 URL

- 前端展示逻辑：
  - 每 2 秒调用 `GET /latest_image` 获取最新图片名与时间戳
  - 对应图片的结果通过 `GET /result?filename=<上传文件名>` 轮询
  - 结果生成由后端触发脚本 `model/getShapeVideo1.py` 完成

**主要接口**
- `GET /`：返回前端页面
- `GET /css_files/<path>`：返回 `html/css_files` 下的静态样式
- `GET /uploads/<path>`：返回 `uploads` 下的图片文件
- `GET /latest_image`：获取最新上传图片信息
- `GET /result?filename=...`：获取图片对应的结果文本
- `POST /upload`：接收图片文件（字段 `file`），保存到 `uploads`
- `GET /processors`：列出已加载的处理器（可选）
- `POST /process`：对图片执行指定处理器（可选）
- `GET /download/<filename>`：下载 `uploads` 下的文件

**注意事项**
- 端口：当前服务运行在 `5401`，不是 `5000`。
- 样式路径：页面使用 `/css_files/sunny.css` 与后端路由保持一致。
- 结果文件命名：`<上传文件名不含扩展>_result.txt`，存放于 `result/`。
  - 后端默认监听 `http://0.0.0.0:5401/`。

- 启动自动处理监控：
  - 在同一环境中运行：
  - `python app.py`
  - 监控输出类似：
    - `开始监控文件夹: uploads (按Ctrl+C停止)`
    - 新图片写入 `uploads/` 后会自动生成 `result/<文件名>_result.txt`。

- 通过网页上传与处理：
  - 打开 `http://localhost:5401/`。
  - 选择图片上传；成功后会显示图片 URL 并出现“选择处理方式”。
  - 处理器目前为占位，点击后会生成一张“处理后”图片，文件名形如：
    - `uploads/digit_recognition_<原始文件名>`（仅复制原图，用于演示流程）。
  - 自动监控脚本会侦测到该新文件，调用算法生成结果 txt 到 `result/`。
---

**配置与路径（app.py）**
- 监控目录：`WATCH_DIR = 'uploads'`。
- 结果目录：`RESULT_DIR = 'result'`。
- 算法脚本：`ALGORITHM_PATH = 'getShapeVideo1.py'`。
---
**PLC段调用（mainself2.py）**
