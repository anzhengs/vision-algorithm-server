from flask import Flask, request, jsonify, send_from_directory, send_file
import os
import io
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
import importlib
import pkgutil


# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # lab401/
HTML_DIR = os.path.join(BASE_DIR, 'html')
HTML_FILES_DIR = os.path.join(HTML_DIR, 'html_files')
CSS_DIR = os.path.join(HTML_DIR, 'css_files')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
RESULT_DIR = os.path.join(BASE_DIR, 'result')
PROCESSORS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processors')

# Ensure upload dir exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Processor plugin system
PROCESSORS = {}


def load_processors():
    global PROCESSORS
    PROCESSORS.clear()
    if not os.path.isdir(PROCESSORS_DIR):
        return
    for finder, name, ispkg in pkgutil.iter_modules([PROCESSORS_DIR]):
        try:
            module = importlib.import_module(f'processors.{name}')
            # Each module should expose PROCESSOR dict: {id, label, description, process(Image, params)->Image}
            meta = getattr(module, 'PROCESSOR', None)
            if meta and all(k in meta for k in ('id', 'label', 'process')):
                PROCESSORS[meta['id']] = meta
        except Exception as e:
            print(f"Failed to load processor '{name}': {e}")


load_processors()


# Routes: HTML & assets
@app.route('/')
def index():
    return send_from_directory(HTML_FILES_DIR, 'index.html')


@app.route('/css_files/<path:path>')
def serve_css(path):
    return send_from_directory(CSS_DIR, path)


@app.route('/uploads/<path:path>')
def serve_uploads(path):
    return send_from_directory(UPLOAD_DIR, path)


# Reuse existing top-level assets folder to avoid duplicating binaries
@app.route('/assets/<path:path>')
def serve_assets(path):
    workspace_root = os.path.dirname(os.path.dirname(BASE_DIR))  # go up to workspace root
    assets_dir = os.path.join(workspace_root, 'html', 'assets')
    return send_from_directory(assets_dir, path)


# API: query result text by uploaded filename
@app.route('/result', methods=['GET'])
def get_result():
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'success': False, 'message': '缺少参数: filename'}), 400

    # derive result file name from uploaded filename
    base, _ = os.path.splitext(filename)
    result_name = f"{base}_result.txt"
    result_path = os.path.join(RESULT_DIR, result_name)

    if not os.path.exists(result_path):
        return jsonify({'success': True, 'ready': False})

    try:
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()
        mtime = os.path.getmtime(result_path)
        return jsonify({
            'success': True,
            'ready': True,
            'filename': result_name,
            'content': content,
            'updated_at': mtime
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'读取结果失败: {str(e)}'}), 500


# API: list processors
@app.route('/processors', methods=['GET'])
def list_processors():
    return jsonify({
        'success': True,
        'processors': [
            {
                'id': p['id'],
                'label': p.get('label', p['id']),
                'description': p.get('description', '')
            } for p in PROCESSORS.values()
        ]
    })


# API: upload image
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': '没有文件部分'})
    f = request.files['image']
    if not f.filename:
        return jsonify({'success': False, 'message': '没有选择文件'})
    if not allowed_file(f.filename):
        return jsonify({'success': False, 'message': '不允许的文件类型'})

    filename = secure_filename(f.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    unique = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(UPLOAD_DIR, unique)
    f.save(save_path)

    return jsonify({
        'success': True,
        'message': '文件上传成功',
        'url': f"/uploads/{unique}",
        'filename': unique
    })


# API: process image by processor id
@app.route('/process', methods=['POST'])
def process_image():
    data = request.get_json(silent=True) or {}
    filename = data.get('filename')
    proc_id = data.get('processor_id')
    params = data.get('params') or {}

    if not filename or not proc_id:
        return jsonify({'success': False, 'message': '缺少必要参数 filename 或 processor_id'})
    if proc_id not in PROCESSORS:
        return jsonify({'success': False, 'message': f'未找到处理器: {proc_id}'})

    src_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(src_path):
        return jsonify({'success': False, 'message': '图片不存在'})

    try:
        with Image.open(src_path) as img:
            processed = PROCESSORS[proc_id]['process'](img, params)

        # Derive extension from original name; default to PNG if unknown
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'png'
        out_name = f"{proc_id}_{filename}"
        out_path = os.path.join(UPLOAD_DIR, out_name)
        processed.save(out_path)

        return jsonify({
            'success': True,
            'message': '图片处理成功',
            'url': f"/uploads/{out_name}",
            'filename': out_name
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'处理图片时出错: {str(e)}'})


# API: download as attachment
@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': '文件不存在'}), 404
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    # Run dev server for local preview
    app.run(host='0.0.0.0', port=5000, debug=True)
