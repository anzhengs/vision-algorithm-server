import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 配置路径（根据你的实际环境修改）
WATCH_DIR = "/home/sazuser/lab401/uploads"  # 待监控的图片文件夹
RESULT_DIR = "/home/sazuser/lab401/results"  # 结果输出文件夹
ALGORITHM_PATH = "/home/sazuser/shape_algorithm/getShapeVideo1.py"  # 算法脚本路径
VENV_ACTIVATE = "/home/sazuser/torch-env/bin/activate"  # 虚拟环境激活脚本

# 支持的图片格式
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp'}


class NewImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        # 只处理文件，忽略文件夹
        if event.is_directory:
            return
        
        file_path = event.src_path
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # 只处理支持的图片格式
        if file_ext not in SUPPORTED_FORMATS:
            print(f"跳过非图片文件: {file_path}")
            return
        
        # 等待文件完全上传（避免读取不完整的文件）
        if not self.wait_for_file_ready(file_path):
            print(f"文件处理失败: {file_path}")
            return
        
        # 调用算法处理图片
        self.process_image(file_path)

    def wait_for_file_ready(self, file_path, timeout=20):
        """等待文件写入完成（通过文件大小稳定判断）"""
        start_time = time.time()
        prev_size = -1
        while time.time() - start_time < timeout:
            if not os.path.exists(file_path):
                return False  # 文件被删除
            current_size = os.path.getsize(file_path)
            if current_size == prev_size:
                return True  # 文件大小稳定，写入完成
            prev_size = current_size
            time.sleep(0.5)
        return False  # 超时

    def process_image(self, image_path):
        """调用算法处理图片并保存结果（修复shell环境问题）"""
        try:
            # 提取文件名（用于结果文件命名）
            file_name = os.path.splitext(os.path.basename(image_path))[0]
            result_file = os.path.join(RESULT_DIR, f"{file_name}_result.txt")

            # 关键修复：用bash执行命令（支持source），并显式指定环境变量
            cmd = f"""
                bash -c '
                    source {VENV_ACTIVATE} && \
                    python {ALGORITHM_PATH} \
                    --input "{image_path}" \
                    --output "{result_file}"
                '
            """

            # 执行命令并捕获输出
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                print(f"处理成功: {image_path} → 结果保存至 {result_file}")
            else:
                print(f"算法错误: {result.stderr}")
                with open(result_file, "w") as f:
                    f.write(f"错误: {result.stderr}")

        except Exception as e:
            error_msg = f"处理失败: {str(e)}"
            print(error_msg)
            with open(result_file, "w") as f:
                f.write(error_msg)


if __name__ == "__main__":
    # 启动监控
    observer = Observer()
    observer.schedule(NewImageHandler(), WATCH_DIR, recursive=False)
    observer.start()
    print(f"开始监控文件夹: {WATCH_DIR} (按Ctrl+C停止)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
