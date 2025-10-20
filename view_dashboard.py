"""Playwright script to view and test the analytics dashboard"""

import time
from playwright.sync_api import sync_playwright

def main():
    print("[INFO] Starting Playwright browser to view dashboard...")
    
    with sync_playwright() as p:
        # Launch browser in headed mode (visible)
        browser = p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        
        # Create a new context with viewport
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        # Create a new page
        page = context.new_page()
        
        # Listen to console messages
        def handle_console(msg):
            if msg.type == 'error':
                print(f"[BROWSER ERROR] {msg.text}")
            elif msg.type == 'warning':
                print(f"[BROWSER WARNING] {msg.text}")
        
        page.on("console", handle_console)
        
        # Listen to page errors
        def handle_page_error(error):
            print(f"[PAGE ERROR] {error}")
        
        page.on("pageerror", handle_page_error)
        
        try:
            print("[INFO] Navigating to dashboard...")
            page.goto("http://localhost:5173/dashboard", wait_until="networkidle", timeout=10000)
            
            print("[SUCCESS] Dashboard loaded!")
            print("[INFO] Taking screenshot...")
            page.screenshot(path="dashboard_screenshot.png")
            print("[SUCCESS] Screenshot saved to dashboard_screenshot.png")
            
            # Check for specific elements
            print("\n[INFO] Checking dashboard elements...")
            
            # Wait for the dashboard to load
            page.wait_for_timeout(2000)
            
            # Get page title
            title = page.title()
            print(f"[INFO] Page title: {title}")
            
            # Check if there are any visible error messages
            errors = page.locator('text=/error/i').all()
            if errors:
                print(f"[WARNING] Found {len(errors)} error messages on page")
            else:
                print("[SUCCESS] No error messages found")
            
            print("\n" + "="*60)
            print("[INFO] Browser window is open for viewing")
            print("[INFO] The dashboard is displayed at: http://localhost:5173/dashboard")
            print("[INFO] Press Ctrl+C to close the browser...")
            print("="*60 + "\n")
            
            # Keep the browser open for viewing
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n[INFO] Closing browser...")
        except Exception as e:
            print(f"[ERROR] Failed to load dashboard: {e}")
            print("[INFO] Make sure the dashboard is running on http://localhost:5173")
            print("[INFO] Run: cd analytics-dashboard && npm run dev")
            
            # Take screenshot of error page
            try:
                page.screenshot(path="dashboard_error.png")
                print("[INFO] Error screenshot saved to dashboard_error.png")
            except:
                pass
        finally:
            browser.close()

if __name__ == "__main__":
    main()


