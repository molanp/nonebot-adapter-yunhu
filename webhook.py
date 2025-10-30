# webhook.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from urllib.parse import parse_qs, urlparse

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 获取请求路径
        path = self.path
        
        # 解析URL以获取查询参数
        parsed_url = urlparse(path)
        params = parse_qs(parsed_url.query)
        # 将参数值从列表转为单个值（如果只有一个值）
        params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
        
        # 获取请求体长度
        content_length = int(self.headers.get('Content-Length', 0))
        
        # 读取请求体
        post_data = self.rfile.read(content_length)
        
        # 解析请求体
        body = {}
        if post_data:
            try:
                # 尝试解析JSON
                body = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                # 如果不是JSON，保存原始数据
                body = {"raw_data": post_data.decode('utf-8')}
        
        # 打印接收到的信息
        print("Received webhook:")
        print(f"Path: {parsed_url.path}")
        print(f"Params: {params}")
        print(f"Body: {body}")
        print("-" * 40)
        
        # 发送响应
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"status": "success"}
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, WebhookHandler)
    print(f"Starting webhook server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()