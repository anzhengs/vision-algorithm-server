import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 配置路径：锚定到项目根目录，避免受启动目录(CWD)影响
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根目录
MODEL_DIR = os.path.join(BASE_DIR, "model")
WATCH_DIR = os.path.join(BASE_DIR, "uploads")  # 待监控的图片文件夹（绝对路径）
RESULT_DIR = os.path.join(BASE_DIR, "result")   # 结果输出文件夹（绝对路径）
ALGORITHM_PATH = os.path.join(MODEL_DIR, "getShapeVideo1.py")  # 算法脚本绝对路径

# 支持的图片格式
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp'}

# 保证监控与结果目录存在（绝对路径）
os.makedirs(WATCH_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)


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
        """调用算法处理图片并保存结果（跨平台修复，保证路径与目录正确）"""
        # 统一绝对路径，避免相对路径在子进程中偏移
        file_name = os.path.splitext(os.path.basename(image_path))[0]
        src_abs = os.path.abspath(image_path)
        out_dir_abs = RESULT_DIR  # 已是绝对路径
        os.makedirs(out_dir_abs, exist_ok=True)
        result_file = os.path.join(out_dir_abs, f"{file_name}_result.txt")

        try:
            # Windows：直接使用当前 Python 解释器，无需 bash/conda activate
            if os.name == 'nt':
                cmd = [
                    sys.executable,
                    ALGORITHM_PATH,
                    "--input", src_abs,
                    "--output", result_file,
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            else:
                # Linux/macOS：优先使用当前解释器；如需激活虚拟环境，请在启动本脚本前完成
                cmd = [
                    sys.executable,
                    ALGORITHM_PATH,
                    "--input", src_abs,
                    "--output", result_file,
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0 and os.path.exists(result_file):
                print(f"处理成功: {image_path} → 结果保存至 {result_file}")
            else:
                # 优先使用 stderr；为空则回退到 stdout；都为空则未知错误
                stderr = (result.stderr or '').strip()
                stdout = (result.stdout or '').strip()
                err_msg = stderr if stderr else (stdout if stdout else "未知错误")
                print(f"算法错误: {err_msg}")
                # 若算法已写出结果文件（例如写入了'处理失败:'的内容），不覆盖，仅在缺失时补写
                if not (os.path.exists(result_file) and os.path.getsize(result_file) > 0):
                    try:
                        with open(result_file, "w", encoding="utf-8") as f:
                            f.write(f"错误: {err_msg}")
                    except Exception as write_err:
                        print(f"写入错误结果失败: {write_err}")

        except Exception as e:
            error_msg = f"处理失败: {str(e)}"
            print(error_msg)
            try:
                with open(result_file, "w", encoding="utf-8") as f:
                    f.write(error_msg)
            except Exception as write_err:
                print(f"写入错误结果失败: {write_err}")


if __name__ == "__main__":
    # 启动监控
    # 再次确保目录存在
    os.makedirs(WATCH_DIR, exist_ok=True)
    os.makedirs(RESULT_DIR, exist_ok=True)
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
