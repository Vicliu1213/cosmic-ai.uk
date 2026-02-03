#!/usr/bin/env python3
"""
文件接收服务器 - 接收上传的文件
支持上传压缩文件、图片等任何类型文件
"""

import os
import http.server
import socketserver
import urllib.parse
from pathlib import Path

class FileUploadHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>文件上传服务器</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background-color: #1a1a1a;
            color: #e0e0e0;
        }
        .upload-area { 
            border: 2px dashed #555; 
            border-radius: 10px; 
            padding: 40px; 
            text-align: center; 
            margin: 20px 0;
            background-color: #2d2d2d;
        }
        .upload-area:hover { border-color: #4a9eff; }
        input[type="file"] { margin: 20px 0; }
        button { 
            background: #4a9eff; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer;
        }
        button:hover { background: #3a8eef; }
        .file-list { margin: 20px 0; }
        .file-item { 
            background: #2d2d2d; 
            padding: 10px; 
            margin: 5px 0; 
            border-radius: 5px;
            border: 1px solid #444;
        }
        a {
            color: #4a9eff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        h1, h3 {
            color: #ffffff;
        }
    </style>
</head>
<body>
    <h1>📁 文件上传服务器</h1>
    <p>上传文件给AI查看 - 支持压缩文件、图片、代码等任何类型</p>
    
    <div class="upload-area">
        <h3>📤 选择文件上传</h3>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" multiple><br><br>
            <button type="submit">上传文件</button>
        </form>
    </div>
    
    <div class="file-list">
        <h3>📋 已上传的文件：</h3>
        <div id="fileList">
            <!-- 文件列表将通过JavaScript动态更新 -->
        </div>
    </div>
    
    <script>
        // 页面加载时刷新文件列表
        window.onload = function() {
            updateFileList();
        };
        
        function updateFileList() {
            fetch('/files')
                .then(response => response.json())
                .then(files => {
                    const fileList = document.getElementById('fileList');
                    fileList.innerHTML = '';
                    
                    if (files.length === 0) {
                        fileList.innerHTML = '<p>暂无上传文件</p>';
                        return;
                    }
                    
                    files.forEach(file => {
                        const fileItem = document.createElement('div');
                        fileItem.className = 'file-item';
                        fileItem.innerHTML = `
                            <strong>${file.name}</strong> 
                            (${file.size}) - 
                            <a href="/uploads/${file.name}" target="_blank">查看</a>
                        `;
                        fileList.appendChild(fileItem);
                    });
                });
        }
    </script>
</body>
</html>
            '''
            self.wfile.write(html.encode('utf-8'))
        
        elif self.path == '/files':
            uploads_dir = Path('uploads')
            if not uploads_dir.exists():
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write('[]'.encode())
                return
            
            files = []
            for file_path in uploads_dir.iterdir():
                if file_path.is_file():
                    files.append({
                        'name': file_path.name,
                        'size': self.format_file_size(file_path.stat().st_size),
                        'path': str(file_path)
                    })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            import json
            self.wfile.write(json.dumps(files).encode('utf-8'))
        
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/upload':
            try:
                content_type = self.headers.get('Content-Type', '')
                if not content_type.startswith('multipart/form-data'):
                    self.send_error(400, "需要multipart/form-data")
                    return
                
                uploads_dir = Path('uploads')
                uploads_dir.mkdir(exist_ok=True)
                
                boundary = content_type.split('boundary=')[1].encode()
                boundary = content_type.split('boundary=')[1].encode()
                content_length = self.headers.get('Content-Length', '0')
                data = self.rfile.read(int(content_length))
                
                parts = data.split(b'--' + boundary)
                
                for part in parts:
                    if b'Content-Disposition' in part and b'filename=' in part:
                        headers_end = part.find(b'\r\n\r\n')
                        headers = part[:headers_end].decode('utf-8', errors='ignore')
                        
                        filename_start = headers.find('filename="') + 10
                        filename_end = headers.find('"', filename_start)
                        filename = headers[filename_start:filename_end]
                        
                        if filename:
                            file_content = part[headers_end + 4:].rstrip(b'\r\n')
                            
                            file_path = uploads_dir / filename
                            with open(file_path, 'wb') as f:
                                f.write(file_content)
                            
                            print(f"✅ 文件已保存: {file_path}")
                
                self.send_response(302)
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
                
            except Exception as e:
                print(f"❌ 上传错误: {e}")
                self.send_error(500, f"上传失败: {e}")
    
    def format_file_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

def main():
    PORT = 8000
    
    print("🚀 启动文件上传服务器...")
    print(f"📡 服务器地址: http://localhost:{PORT}")
    print("📁 上传的文件将保存在 'uploads/' 目录")
    print("🔧 按 Ctrl+C 停止服务器")
    print()
    
    with socketserver.TCPServer(("", PORT), FileUploadHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务器已停止")

if __name__ == "__main__":
    main()