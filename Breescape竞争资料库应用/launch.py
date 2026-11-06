from pathlib import Path
import urllib.request, json, subprocess, time, sys, hashlib
ROOT=Path(__file__).resolve().parent
expected=hashlib.sha256(str(ROOT/'data'/'library.sqlite3').encode()).hexdigest()[:12]
def check(port):
 try:
  with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health',timeout=.5) as r:
   data=json.load(r);return data.get('app')=='breescape-library-v1' and data.get('database')==expected
 except Exception:return False
for port in range(8766,8776):
 if check(port):subprocess.run(['open',f'http://127.0.0.1:{port}']);sys.exit(0)
import socket
for port in range(8766,8776):
 with socket.socket() as s:
  s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
  try:s.bind(('127.0.0.1',port))
  except OSError:continue
 break
else:raise RuntimeError('本地端口正被占用，请关闭其他资料库窗口后重试')
(ROOT/'data').mkdir(exist_ok=True)
with (ROOT/'data'/'server.log').open('ab') as log:
 subprocess.Popen([sys.executable,str(ROOT/'server.py'),'--port',str(port)],stdin=subprocess.DEVNULL,stdout=log,stderr=log,cwd=ROOT,start_new_session=True)
for _ in range(50):
 if check(port):subprocess.run(['open',f'http://127.0.0.1:{port}']);break
 time.sleep(.15)
else:raise RuntimeError('未能启动资料库，请查看data/server.log')
