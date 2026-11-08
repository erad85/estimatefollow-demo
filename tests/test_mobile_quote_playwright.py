"""End-to-end mobile quote regression in Chromium: catch offscreen Save controls."""
import functools
import http.server
import os
import socketserver
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
STORE_KEY = 'estimatefollow_v01_demo'

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def run():
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    with ReusableTCPServer(('127.0.0.1', 0), handler) as server:
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as playwright:
                options = {'headless': True, 'args': ['--no-sandbox']}
                if os.environ.get('CHROMIUM_BIN'):
                    options['executable_path'] = os.environ['CHROMIUM_BIN']
                browser = playwright.chromium.launch(**options)
                try:
                    for width, height in ((360, 400), (384, 720), (412, 915)):
                        context = browser.new_context(viewport={'width': width, 'height': height}, is_mobile=True, has_touch=True, device_scale_factor=2)
                        page = context.new_page()
                        errors = []
                        page.on('pageerror', lambda exc: errors.append(str(exc)))
                        page.goto(f'http://127.0.0.1:{port}/index.html', wait_until='domcontentloaded')
                        page.locator('#newBtn').click()
                        assert page.locator('#createOverlay').evaluate('(e) => e.classList.contains("open")')
                        top = page.locator('#createSaveTopBtn')
                        top.wait_for(state='visible')
                        bounds = top.bounding_box()
                        assert bounds and 0 <= bounds['y'] and bounds['y'] + bounds['height'] <= height + 1, ('save offscreen', width, height, bounds)
                        page.locator('#newName').fill(f'Test Contractor {height}')
                        page.locator('#newJob').fill('Deck repair')
                        page.locator('#newAmount').fill('1450')
                        page.locator('#newNotes').fill('Test note: long form input')
                        short_height = max(260, height - 200)
                        page.set_viewport_size({'width': width, 'height': short_height})
                        bounds = top.bounding_box()
                        assert bounds and 0 <= bounds['y'] and bounds['y'] + bounds['height'] <= short_height + 1, ('save offscreen after keyboard', width, height, bounds)
                        top.click()
                        assert not page.locator('#createOverlay').evaluate('(e) => e.classList.contains("open")'), ('form failed submit', width, height)
                        state = page.evaluate(f'JSON.parse(localStorage.getItem("{STORE_KEY}"))')
                        assert any(x.get('name') == f'Test Contractor {height}' for x in state['leads']), ('not saved', width, height)
                        page.reload(wait_until='domcontentloaded')
                        state = page.evaluate(f'JSON.parse(localStorage.getItem("{STORE_KEY}"))')
                        assert any(x.get('name') == f'Test Contractor {height}' for x in state['leads']), ('not persisted', width, height)
                        assert not errors, ('JavaScript errors', width, height, errors)
                        print(f'PASS: quote save / reload {width}x{height} with keyboard viewport {short_height}')
                        context.close()
                finally:
                    browser.close()
        finally:
            server.shutdown()

if __name__ == '__main__':
    run()
