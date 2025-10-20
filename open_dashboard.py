"""Simple script to open dashboard in browser"""

import time
from playwright.sync_api import sync_playwright

print("[INFO] Opening dashboard in browser...")
print("[INFO] Waiting for server to be ready...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=['--start-maximized'])
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    
    # Try multiple times with delays
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            print(f"[INFO] Attempt {attempt + 1}/{max_attempts}: Trying to connect...")
            page.goto("http://localhost:5173/dashboard", timeout=5000)
            print("[SUCCESS] Dashboard loaded!")
            break
        except Exception as e:
            if attempt < max_attempts - 1:
                print(f"[WAIT] Server not ready yet, waiting 3 seconds...")
                time.sleep(3)
            else:
                print(f"[ERROR] Could not connect after {max_attempts} attempts")
                print("[INFO] Trying root path instead...")
                try:
                    page.goto("http://localhost:5173/", timeout=5000)
                    print("[SUCCESS] Root page loaded!")
                    print("[INFO] Navigate to /dashboard manually in the browser")
                except:
                    print("[ERROR] Could not connect to server at all")
                    browser.close()
                    exit(1)
    
    page.screenshot(path="dashboard_view.png")
    print("[SUCCESS] Screenshot saved!")
    print("\n" + "="*60)
    print("[INFO] Browser is open - you can now interact with the dashboard")
    print("[INFO] Press Ctrl+C to close...")
    print("="*60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Closing browser...")
    finally:
        browser.close()

