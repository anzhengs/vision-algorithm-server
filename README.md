# 视觉算法自动处理服务器项目
基于ProxmoxVE虚拟机的视觉算法部署方案，实现监控指定文件夹，自动处理新传入的图片并生成结果。

## 核心功能
- 实时监控 `uploads/` 文件夹，新图片传入后自动触发算法处理
- 处理结果保存到 `results/` 文件夹（文本格式）
- 支持图片格式：jpg、jpeg、png、bmp

## 环境依赖
- Python 3.8+
- 依赖包：torch、opencv-python、watchdog、flask 等（见 requirements.txt）

## 使用步骤
1. 克隆仓库：`git clone https://github.com/anzhengs/vision-algorithm-server.git`
2. 激活虚拟环境：`source torch-env/bin/activate`
3. 安装依赖：`pip install -r requirements.txt`
4. 启动监控：`python auto_process.py`# vision-algorithm-server
视觉算法服务器配置与自动处理脚本
