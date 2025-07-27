from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import subprocess
import threading
import re
import os
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import webview
import ctypes
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wallpaper_engine_downloader_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    'steam_username': 'ruiiixx',
    'steam_password': 'S67GBTB83D3Y',
    'wallpaper_engine_path': 'C:/Program Files (x86)/Steam/steamapps/common/wallpaper_engine/projects/myprojects',
    'depot_downloader_path': './DepotDownloaderMod/DepotDownloader.exe',
    'dark_mode': False
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def extract_workshop_id(url):
    patterns = [
        r'steamcommunity\.com/sharedfiles/filedetails/\?id=(\d+)',
        r'steamcommunity\.com/workshop/filedetails/\?id=(\d+)',
        r'id=(\d+)',
        r'^(\d+)$'
    ]
    for pattern in patterns:
        match = re.search(pattern, str(url))
        if match:
            return match.group(1)
    return None

def get_workshop_info(workshop_id):
    try:
        url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title_elem = soup.find('div', class_='workshopItemTitle')
            title = title_elem.text.strip() if title_elem else f"Workshop Item {workshop_id}"
            preview_elem = soup.find('img', id='previewImage')
            if not preview_elem:
                preview_elem = soup.select_one('.workshopItemPreviewImage img')
            preview_url = preview_elem['src'] if preview_elem else None
            return {'id': workshop_id, 'title': title, 'preview_url': preview_url, 'url': url}
        return {'id': workshop_id, 'title': f"Workshop Item {workshop_id}", 'preview_url': None, 'url': url}
    except Exception as e:
        print(f"Error fetching workshop info: {e}")
        return {'id': workshop_id, 'title': f"Workshop Item {workshop_id}", 'preview_url': None, 'url': f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"}

def search_workshop(query, sort='trend', page=1):
    try:
        url = f"https://steamcommunity.com/workshop/browse/"
        params = {
            'appid': '431960',
            'searchtext': query if query else '',
            'childpublishedfileid': '0',
            'browsesort': sort,
            'actualsort': sort,
            'section': 'readytouseitems',
            'created_date_range_filter_start': '0',
            'created_date_range_filter_end': '0',
            'updated_date_range_filter_start': '0',
            'updated_date_range_filter_end': '0',
            'p': page,
        }
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            items = []
            
            workshop_items = soup.find_all('div', class_='workshopItem')
            for item in workshop_items:
                try:
                    link_elem = item.find('a', class_='ugc')
                    if link_elem and 'href' in link_elem.attrs:
                        item_url = link_elem['href']
                        workshop_id = extract_workshop_id(item_url)
                        
                        if workshop_id:
                            title_elem = item.find('div', class_='workshopItemTitle')
                            title = title_elem.text.strip() if title_elem else f"Workshop Item {workshop_id}"
                            
                            img_elem = item.find('img')
                            preview_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else None
                            
                            author_elem = item.find('div', class_='workshopItemAuthorName')
                            author = author_elem.text.strip() if author_elem else "Unknown"
                            
                            items.append({
                                'id': workshop_id,
                                'title': title,
                                'author': author,
                                'preview_url': preview_url,
                                'url': item_url
                            })
                except Exception as e:
                    continue
            
            return items
        return []
    except Exception as e:
        print(f"Search error: {e}")
        return []

@app.route('/')
def index():
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        new_config = {
            'steam_username': request.form.get('steam_username', ''),
            'steam_password': request.form.get('steam_password', ''),
            'wallpaper_engine_path': request.form.get('wallpaper_engine_path', DEFAULT_CONFIG['wallpaper_engine_path']),
            'depot_downloader_path': request.form.get('depot_downloader_path', DEFAULT_CONFIG['depot_downloader_path']),
            'dark_mode': request.form.get('dark_mode') == 'on' 
        }
        save_config(new_config)
        return jsonify({'success': True, 'message': 'Configuration saved successfully!'})
    config = load_config()
    return render_template('config.html', config=config)

@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.get_json()
    query = data.get('query', '').strip()
    sort = data.get('sort', 'trend')
    page = data.get('page', 1)
    
    try:
        results = search_workshop(query, sort, page)
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dark-mode', methods=['GET', 'POST'])
def api_dark_mode():
    if request.method == 'POST':
        data = request.get_json()
        dark_mode = data.get('dark_mode', False)
        
        config = load_config()
        config['dark_mode'] = dark_mode
        save_config(config)
        
        return jsonify({'success': True, 'dark_mode': dark_mode})
    else:
        config = load_config()
        return jsonify({'dark_mode': config.get('dark_mode', False)})

@app.route('/test_config', methods=['POST'])
def test_config():
    try:
        config = load_config()
        issues = []
        warnings = []
        
        depot_path = config.get('depot_downloader_path', '')
        if not depot_path:
            issues.append("DepotDownloader path not configured")
        elif not os.path.exists(depot_path):
            issues.append(f"DepotDownloader not found at: {depot_path}")
        else:
            try:
                result = subprocess.run([depot_path, '-help'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0 or 'DepotDownloader' in result.stdout:
                    warnings.append(f"DepotDownloader executable works: {depot_path}")
                else:
                    warnings.append("DepotDownloader may not be working correctly")
            except subprocess.TimeoutExpired:
                warnings.append("DepotDownloader is slow to respond")
            except Exception as e:
                issues.append(f"Error testing DepotDownloader: {e}")
        
        username = config.get('steam_username', '')
        password = config.get('steam_password', '')
        if not username:
            issues.append("Steam username not configured")
        else:
            warnings.append(f"Steam username configured: {username}")
        if not password:
            issues.append("Steam password not configured")
        else:
            warnings.append("Steam password configured")
        
        we_path = config.get('wallpaper_engine_path', '')
        if not we_path:
            issues.append("Wallpaper Engine path not configured")
        else:
            try:
                if not os.path.exists(we_path):
                    os.makedirs(we_path, exist_ok=True)
                    warnings.append(f"Created Wallpaper Engine directory: {we_path}")
                else:
                    warnings.append(f"Wallpaper Engine directory exists: {we_path}")
                test_file = os.path.join(we_path, 'test_write.tmp')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    warnings.append("Write permissions OK for Wallpaper Engine directory")
                except Exception:
                    issues.append("Cannot write to Wallpaper Engine directory")
            except Exception as e:
                issues.append(f"Error with Wallpaper Engine path: {e}")
        
        if issues:
            return jsonify({'success': False, 'message': f'Configuration has {len(issues)} issue(s)', 'issues': issues, 'warnings': warnings})
        else:
            return jsonify({'success': True, 'message': 'Configuration looks good!', 'warnings': warnings})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error testing configuration: {str(e)}'})

@app.route('/parse_workshop', methods=['POST'])
def parse_workshop():
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({'error': 'URL is required'})
    
    workshop_id = extract_workshop_id(url)
    if not workshop_id:
        return jsonify({'error': 'Invalid workshop URL or ID'})
    
    workshop_info = get_workshop_info(workshop_id)
    if workshop_info:
        return jsonify(workshop_info)
    else:
        return jsonify({'error': 'Could not fetch workshop information'})

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    workshop_id = data.get('workshop_id')
    
    if not workshop_id:
        return jsonify({'success': False, 'error': 'Workshop ID is required'})
    
    config = load_config()
    if not config.get('steam_username') or not config.get('steam_password'):
        return jsonify({'success': False, 'error': 'Steam credentials not configured. Please check settings.'})
    
    if not os.path.exists(config.get('depot_downloader_path', '')):
        return jsonify({'success': False, 'error': 'DepotDownloader not found. Please check settings.'})
    
    thread = threading.Thread(target=download_workshop_item, args=(workshop_id, config))
    thread.start()
    
    return jsonify({'success': True, 'message': 'Download started'})

def download_workshop_item(workshop_id, config):
    try:
        socketio.emit('download_status', {'workshop_id': workshop_id, 'status': 'starting', 'message': f'Starting download for workshop item {workshop_id}...'})
        
        depot_path = config.get('depot_downloader_path', '')
        if not depot_path or not os.path.exists(depot_path):
            raise Exception("DepotDownloader path not configured or not found")
        
        username = config.get('steam_username', '')
        password = config.get('steam_password', '')
        if not username or not password:
            raise Exception("Steam credentials not configured")
        
        wallpaper_path = config.get('wallpaper_engine_path', '')
        if not wallpaper_path:
            raise Exception("Wallpaper Engine path not configured")
        
        download_path = os.path.join(wallpaper_path, workshop_id)
        os.makedirs(download_path, exist_ok=True)
        
        cmd = [depot_path, '-app', '431960', '-pubfile', workshop_id, '-verify-all', '-username', username, '-password', password, '-dir', download_path]
        
        socketio.emit('download_status', {'workshop_id': workshop_id, 'status': 'running', 'message': 'Running DepotDownloader...'})
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True, cwd=os.path.dirname(depot_path) if os.path.dirname(depot_path) else None)
        
        for line in iter(process.stdout.readline, ''):
            if line:
                line = line.strip()
                socketio.emit('download_output', {'workshop_id': workshop_id, 'output': line})
                
                if '%' in line:
                    try:
                        progress_match = re.search(r'(\d+(?:\.\d+)?)%', line)
                        if progress_match:
                            progress = float(progress_match.group(1))
                            socketio.emit('download_progress', {'workshop_id': workshop_id, 'progress': progress})
                    except:
                        pass
        
        process.wait(timeout=300)
        
        if process.returncode == 0:
            downloaded_files = []
            try:
                for root, dirs, files in os.walk(download_path):
                    downloaded_files.extend(files)
            except:
                pass
            
            if downloaded_files:
                socketio.emit('download_status', {'workshop_id': workshop_id, 'status': 'completed', 'message': f'Download completed! {len(downloaded_files)} files downloaded.', 'download_path': download_path})
            else:
                socketio.emit('download_status', {'workshop_id': workshop_id, 'status': 'error', 'message': 'Download completed but no files found.'})
        else:
            error_messages = {
                1: "General error - Check DepotDownloader logs",
                2: "Login failed - Check Steam credentials",
                3: "Workshop item not found or access denied",
                5: "Network error - Check internet connection",
                86: "Invalid workshop ID format",
                87: "Steam Guard required"
            }
            error_msg = error_messages.get(process.returncode, f"Download failed with error code {process.returncode}")
            socketio.emit('download_status', {'workshop_id': workshop_id, 'status': 'error', 'message': error_msg})
            
    except Exception as e:
        socketio.emit('download_status', {'workshop_id': workshop_id, 'status': 'error', 'message': str(e)})

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def check_dependencies():
    missing_deps = []
    try:
        import flask
        print("✅ Flask available")
    except ImportError as e:
        missing_deps.append(f"Flask: {e}")
    try:
        import flask_socketio
        print("✅ Flask-SocketIO available")
    except ImportError as e:
        missing_deps.append(f"Flask-SocketIO: {e}")
    try:
        import requests
        print("✅ Requests available")
    except ImportError as e:
        missing_deps.append(f"Requests: {e}")
    try:
        import bs4
        print("✅ BeautifulSoup4 available")
    except ImportError as e:
        missing_deps.append(f"BeautifulSoup4: {e}")
    try:
        import webview
        print("✅ PyWebView available")
    except ImportError as e:
        missing_deps.append(f"PyWebView: {e}")
    
    if missing_deps:
        print("\n❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nPlease install missing dependencies with:")
        print("pip install -r requirements.txt")
        return False
    return True

def check_port_availability(port=5001):
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            print(f"✅ Port {port} is available")
            return True
    except socket.error as e:
        print(f"❌ Port {port} is in use: {e}")
        return False

def test_flask_server():
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://127.0.0.1:5001/', timeout=2)
            if response.status_code == 200:
                print(f"✅ Flask server ready (attempt {attempt + 1})")
                return True
        except requests.exceptions.RequestException:
            print(f"⏳ Waiting for Flask server... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(1)
    print("❌ Flask server failed to start properly")
    return False

def check_system_requirements():
    print("\n🖥️ System Information:")
    import platform
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")
    print(f"   Python: {platform.python_version()}")
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"   RAM: {memory.total // (1024**3)} GB total, {memory.available // (1024**3)} GB available")
    except ImportError:
        print("   RAM: Could not determine")
    try:
        import webview
        print(f"   WebView: Available")
        if platform.system() == 'Windows':
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}")
                version = winreg.QueryValueEx(key, "pv")[0]
                print(f"   WebView2: {version}")
                winreg.CloseKey(key)
            except:
                print("   WebView2: Not detected")
    except ImportError:
        print("   WebView: Not available")
    return True

if __name__ == '__main__':
    config = load_config()

    print("🎨 Wallpaper Engine Workshop Downloader")
    print("=" * 50)
    config
    try:
        import sys
        if sys.version_info < (3, 7):
            print(f"❌ Python 3.7+ required. Current version: {sys.version}")
            input("Press Enter to exit...")
            sys.exit(1)
        else:
            print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        
        check_system_requirements()
        
        print("\n🔍 Checking dependencies...")
        if not check_dependencies():
            input("Press Enter to exit...")
            sys.exit(1)
        
        print("\n🔌 Checking port availability...")
        if not check_port_availability(5001):
            print("💡 Port 5001 is already in use. This might cause issues.")
            choice = input("Continue anyway? (y/N): ").lower().strip()
            if choice != 'y':
                sys.exit(1)
        
        print("\n📁 Creating directories...")
        try:
            os.makedirs('templates', exist_ok=True)
            os.makedirs('static', exist_ok=True)
            os.makedirs('static/css', exist_ok=True)
            os.makedirs('static/js', exist_ok=True)
            print("✅ Directories created/verified")
        except Exception as e:
            print(f"❌ Failed to create directories: {e}")
            input("Press Enter to exit...")
            sys.exit(1)
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        try:
            if os.name == 'nt':
                ctypes.windll.kernel32.SetConsoleTitleW("Wallpaper Engine Workshop Downloader")
                print("✅ Windows console configured")
        except Exception as e:
            print(f"⚠️ Windows setup warning: {e}")
        
        print("\n🚀 Starting Flask server...")
        
        def start_flask_app():
            try:
                socketio.run(app, debug=False, host='127.0.0.1', port=5001, use_reloader=False)
            except Exception as e:
                print(f"❌ Flask server error: {e}")
        
        flask_thread = threading.Thread(target=start_flask_app, daemon=True)
        flask_thread.start()
        
        if not test_flask_server():
            print("❌ Flask server failed to start.")
            input("Press Enter to exit...")
            sys.exit(1)
        
        print("\n🖥️ Starting desktop application...")
        
        webview_success = False
        try:
            import webview
            window = webview.create_window(title='Glitcheds Wallpaper Engine Workshop Downloader', url='http://127.0.0.1:5001', width=1200, height=800, min_size=(800, 600), resizable=True, maximized=False)
            print("✅ Desktop window created")
            webview.start(debug=False)
            webview_success = True
        except ImportError as e:
            print(f"❌ PyWebView import error: {e}")
        except Exception as e:
            print(f"❌ Desktop window error: {e}")
        
        if not webview_success:
            print("\n💻 Desktop window failed. Opening in web browser...")
            print("🌐 Please open: http://127.0.0.1:5001")
            try:
                import webbrowser
                webbrowser.open('http://127.0.0.1:5001')
            except Exception as e:
                print(f"⚠️ Could not open browser automatically: {e}")
            
            print("\n🔴 Press Enter to stop the server...")
            input()
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        input("Press Enter to exit...")
    finally:
        print("👋 Goodbye!")