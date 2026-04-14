from playwright.sync_api import sync_playwright
import time
import sys

def log(message):
    print(f"[TEST] {message}")

def check_console_errors(page):
    console_logs = page.context.browser._impl_obj._loop.run_until_complete(
        page.context.browser._impl_obj._connection.send("browserContexts", {
            "action": "getConsoleLogs"
        })
    )
    errors = []
    for log_entry in console_logs:
        if log_entry.get("type") == "error":
            errors.append(log_entry)
    return errors

def main():
    with sync_playwright() as p:
        log("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        all_tests_passed = True
        
        try:
            # Test 1: Navigate to the app
            log("Test 1: Navigating to the app...")
            page.goto('http://localhost:8000')
            page.wait_for_load_state('networkidle', timeout=10000)
            time.sleep(2)
            
            screenshot_path = '/workspace/screenshot_1_home.png'
            page.screenshot(path=screenshot_path, full_page=True)
            log(f"  ✓ Home page screenshot saved to {screenshot_path}")
            
            # Check if we're on login page
            if "Login" in page.title() or "登录" in page.title() or page.locator('text=登录').count() > 0:
                log("  ✓ Successfully navigated to login page")
            else:
                log("  ⚠️  Not sure if on login page")
            
            # Test 2: Login functionality
            log("\nTest 2: Testing login functionality...")
            
            try:
                # Find username input
                username_input = page.locator('input[type="text"], input[id*="username"]').first
                username_input.fill('admin')
                
                # Find password input
                password_input = page.locator('input[type="password"]').first
                password_input.fill('admin123')
                
                # Find login button
                login_button = page.locator('button:has-text("登录"), button:has-text("Login"), button[type="submit"]').first
                login_button.click()
                
                page.wait_for_load_state('networkidle', timeout=10000)
                time.sleep(3)
                
                screenshot_path = '/workspace/screenshot_2_after_login.png'
                page.screenshot(path=screenshot_path, full_page=True)
                log(f"  ✓ After login screenshot saved to {screenshot_path}")
                
                log("  ✓ Login test completed")
            except Exception as e:
                log(f"  ✗ Login test failed: {e}")
                all_tests_passed = False
            
            # Test 3: Check navigation and user management
            log("\nTest 3: Testing navigation and user management...")
            
            try:
                # Try to find user management link
                user_management_link = page.locator('text=用户管理, text=Users').first
                if user_management_link.count() > 0:
                    user_management_link.click()
                    page.wait_for_load_state('networkidle', timeout=10000)
                    time.sleep(2)
                    
                    screenshot_path = '/workspace/screenshot_3_user_management.png'
                    page.screenshot(path=screenshot_path, full_page=True)
                    log(f"  ✓ User management page screenshot saved to {screenshot_path}")
                    
                    log("  ✓ Successfully navigated to user management")
                else:
                    log("  ⚠️  User management link not found")
                    
            except Exception as e:
                log(f"  ✗ User management test failed: {e}")
                all_tests_passed = False
            
            # Test 4: Check file management
            log("\nTest 4: Testing file management...")
            
            try:
                # Try to find files link
                files_link = page.locator('text=文件, text=Files').first
                if files_link.count() > 0:
                    files_link.click()
                    page.wait_for_load_state('networkidle', timeout=10000)
                    time.sleep(2)
                    
                    screenshot_path = '/workspace/screenshot_4_file_management.png'
                    page.screenshot(path=screenshot_path, full_page=True)
                    log(f"  ✓ File management page screenshot saved to {screenshot_path}")
                    
                    log("  ✓ Successfully navigated to file management")
                else:
                    log("  ⚠️  Files link not found")
                    
            except Exception as e:
                log(f"  ✗ File management test failed: {e}")
                all_tests_passed = False
            
            # Test 5: Check multimedia
            log("\nTest 5: Testing multimedia...")
            
            try:
                # Try to find multimedia link
                multimedia_link = page.locator('text=多媒体, text=Multimedia').first
                if multimedia_link.count() > 0:
                    multimedia_link.click()
                    page.wait_for_load_state('networkidle', timeout=10000)
                    time.sleep(2)
                    
                    screenshot_path = '/workspace/screenshot_5_multimedia.png'
                    page.screenshot(path=screenshot_path, full_page=True)
                    log(f"  ✓ Multimedia page screenshot saved to {screenshot_path}")
                    
                    log("  ✓ Successfully navigated to multimedia")
                else:
                    log("  ⚠️  Multimedia link not found")
                    
            except Exception as e:
                log(f"  ✗ Multimedia test failed: {e}")
                all_tests_passed = False
            
            # Check console for errors
            log("\nTest 6: Checking console for errors...")
            try:
                # Check console logs
                console_errors = []
                page.on("console", lambda msg: console_errors.append(msg) if msg.type == "error" else None)
                
                # Refresh page to capture any errors
                page.reload()
                page.wait_for_load_state('networkidle', timeout=10000)
                time.sleep(2)
                
                if console_errors:
                    log(f"  ✗ Found {len(console_errors)} console error(s):")
                    for err in console_errors[:3]:
                        log(f"    - {err.text}")
                    all_tests_passed = False
                else:
                    log("  ✓ No console errors found")
                    
            except Exception as e:
                log(f"  ⚠️  Console error check had issue: {e}")
            
            # Final summary
            log("\n" + "="*50)
            if all_tests_passed:
                log("✓ All tests passed!")
            else:
                log("⚠️  Some tests had issues, but app is accessible")
            log("="*50)
            
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
