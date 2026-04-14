from playwright.sync_api import sync_playwright
import time
import sys

def log(message):
    print(f"[TEST] {message}")

def main():
    with sync_playwright() as p:
        log("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        all_tests_passed = True
        console_errors = []
        
        def handle_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)
                log(f"  [CONSOLE ERROR] {msg.text}")
        
        page.on("console", handle_console)
        
        try:
            # Test 1: Navigate to the app
            log("\nTest 1: Navigating to the app...")
            page.goto('http://localhost:8000')
            page.wait_for_load_state('networkidle', timeout=15000)
            time.sleep(3)
            
            screenshot_path = '/workspace/screenshot_1_home.png'
            page.screenshot(path=screenshot_path, full_page=True)
            log(f"  ✓ Screenshot saved to {screenshot_path}")
            
            # Check page title
            title = page.title()
            log(f"  ✓ Page title: {title}")
            
            # Test 2: Check if login page loads
            log("\nTest 2: Checking login page...")
            username_input = page.locator('input[type="text"], input[id*="username"]').first
            password_input = page.locator('input[type="password"]').first
            login_button = page.locator('button:has-text("登录"), button:has-text("Login"), button[type="submit"]').first
            
            if username_input.count() > 0 and password_input.count() > 0:
                log("  ✓ Login form elements found")
                
                # Test login
                log("\nTest 3: Testing login...")
                username_input.fill('admin')
                password_input.fill('admin123')
                
                if login_button.count() > 0:
                    login_button.click()
                    page.wait_for_load_state('networkidle', timeout=15000)
                    time.sleep(3)
                    
                    screenshot_path = '/workspace/screenshot_2_after_login.png'
                    page.screenshot(path=screenshot_path, full_page=True)
                    log(f"  ✓ After login screenshot saved to {screenshot_path}")
                    
                    # Test 4: Check navigation links
                    log("\nTest 4: Checking navigation...")
                    nav_links = page.locator('a, button').all()
                    log(f"  ✓ Found {len(nav_links)} navigation elements")
                    
                    # Try to find and click user management
                    log("\nTest 5: Checking user management...")
                    user_link = page.locator('text=用户管理, text=Users').first
                    if user_link.count() > 0:
                        user_link.click()
                        page.wait_for_load_state('networkidle', timeout=10000)
                        time.sleep(2)
                        
                        screenshot_path = '/workspace/screenshot_3_users.png'
                        page.screenshot(path=screenshot_path, full_page=True)
                        log(f"  ✓ User management screenshot saved to {screenshot_path}")
                    else:
                        log("  ⚠️  User management link not found, checking other links...")
                        # Try files
                        files_link = page.locator('text=文件, text=Files').first
                        if files_link.count() > 0:
                            files_link.click()
                            page.wait_for_load_state('networkidle', timeout=10000)
                            time.sleep(2)
                            
                            screenshot_path = '/workspace/screenshot_3_files.png'
                            page.screenshot(path=screenshot_path, full_page=True)
                            log(f"  ✓ Files screenshot saved to {screenshot_path}")
                else:
                    log("  ⚠️  Login button not found")
            else:
                log("  ⚠️  Login form elements not found, maybe already logged in?")
                # Take screenshot anyway
                screenshot_path = '/workspace/screenshot_2_current.png'
                page.screenshot(path=screenshot_path, full_page=True)
                log(f"  ✓ Screenshot saved to {screenshot_path}")
            
            # Test 6: Check for console errors
            log("\nTest 6: Console errors check...")
            if console_errors:
                log(f"  ✗ Found {len(console_errors)} console error(s)")
                all_tests_passed = False
            else:
                log("  ✓ No console errors found")
            
            # Final summary
            log("\n" + "="*60)
            if all_tests_passed:
                log("✓ All basic tests passed! App is accessible.")
            else:
                log("⚠️  Some tests had issues, but check screenshots for details")
            log("="*60)
            log(f"\nScreenshots saved to /workspace/")
            
        except Exception as e:
            log(f"\n✗ Critical error during testing: {e}")
            import traceback
            traceback.print_exc()
            all_tests_passed = False
        finally:
            log("\nClosing browser...")
            browser.close()
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    sys.exit(main())
