from flask import Flask, request, jsonify
import base64
import os
from datetime import datetime

# 初始化Flask应用
app = Flask(__name__)

# 定义数据存储目录（和算法文件在同一目录，方便算法读取）
UPLOAD_DIR = '/home/sazuser/shape_algorithm/frontend_data'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)  # 若目录不存在，自动创建

# 定义接口：接收前端传来的Base64图片（需确认：路径、请求方法、数据格式）
@app.route('/upload_shape', methods=['POST'])  # 路径：/upload_shape；方法：POST
def upload_shape_data():
    try:
        # 1. 接收前端传来的JSON数据（需确认：前端传的键名，示例为"image_base64"）
        data = request.get_json()
        image_base64 = data.get('image_base64')  # 前端用"image_base64"键传Base64编码
        task_id = data.get('task_id', str(datetime.now().timestamp()))  # 任务ID，默认用时间戳

        # 2. 验证数据是否存在
        if not image_base64:
            return jsonify({'status': 'fail', 'msg': '缺少image_base64数据'})

        # 3. Base64编码转图片并保存到服务器
        image_data = base64.b64decode(image_base64)  # 解码Base64
        image_path = os.path.join(UPLOAD_DIR, f'task_{task_id}_input.png')  # 保存路径
        with open(image_path, 'wb') as f:
            f.write(image_data)

        # 4. 返回成功响应（前端可根据status判断是否上传成功）
        return jsonify({
            'status': 'success',
            'msg': '数据已保存到服务器',
            'image_save_path': image_path,  # 返回保存路径，方便后续调试
            'task_id': task_id
        })

    except Exception as e:
        # 若出错，返回错误信息
        return jsonify({'status': 'fail', 'msg': f'上传失败：{str(e)}'})

# 启动Flask服务（默认端口5000，服务器IP：192.168.40.49）
if __name__ == '__main__':
    # host='0.0.0.0'：允许其他设备（如前端电脑）访问服务器的该接口
    app.run(host='0.0.0.0', port=5000, debug=True)
