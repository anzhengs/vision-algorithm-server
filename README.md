# 视觉算法自动处理服务器

**项目目标**
- 提供一个简洁的网页前端用于图片上传与预览。
- 后端保存上传图片到 `uploads/`，并支持“处理器插件”对图片进行处理与回显。
- 独立监控脚本自动侦测 `uploads/` 新文件，调用算法生成文本结果到 `result/`。
- 再回传到html界面上去(还未实现)
---

**环境准备**
- Python 3.8+
- 依赖包：
  - `flask`, `watchdog`, `Pillow`, `opencv-python`, `torch`（CPU 版即可）。
---

**快速开始**
- 启动后端服务：
  - 在项目根目录运行：
  - `python python/app.py`
  - 后端默认监听 `http://0.0.0.0:5000/`。

- 启动自动处理监控：
  - 在同一环境中运行：
  - `python auto_process.py`
  - 监控输出类似：
    - `开始监控文件夹: uploads (按Ctrl+C停止)`
    - 新图片写入 `uploads/` 后会自动生成 `result/<文件名>_result.txt`。

- 通过网页上传与处理：
  - 打开 `http://localhost:5000/`。
  - 选择图片上传；成功后会显示图片 URL 并出现“选择处理方式”。
  - 处理器目前为占位，点击后会生成一张“处理后”图片，文件名形如：
    - `uploads/digit_recognition_<原始文件名>`（仅复制原图，用于演示流程）。
  - 自动监控脚本会侦测到该新文件，调用算法生成结果 txt 到 `result/`。
---

**配置与路径（auto_process.py）**
- 监控目录：`WATCH_DIR = 'uploads'`。
- 结果目录：`RESULT_DIR = 'result'`。
- 算法脚本：`ALGORITHM_PATH = 'getShapeVideo1.py'`。
---

