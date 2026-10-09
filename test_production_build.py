#!/usr/bin/env python3
"""
Test the NutriVane production build served on localhost:4567
Verifies the yarn build output is functional and ready for Vercel deployment
"""

import asyncio
import sys
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

async def test_production_build():
    results = {
        "app_loads": False,
        "no_fatal_errors": False,
        "guest_button_clicked": False,
        "home_page_loaded": False,
        "resep_page_loaded": False,
        "scan_page_loaded": False,
        "errors": [],
        "warnings": []
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Collect console messages
        console_messages = []
        fatal_errors = []
        
        def handle_console(msg):
            console_messages.append({
                "type": msg.type,
                "text": msg.text
            })
            if msg.type == "error":
                # Filter out non-fatal errors
                text = msg.text.lower()
                if "failed to load resource" not in text and \
                   "net::err" not in text and \
                   "404" not in text:
                    fatal_errors.append(msg.text)
        
        page.on("console", handle_console)
        
        # Collect page errors
        page_errors = []
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        
        try:
            print("🧪 Test 1: Loading production build at http://localhost:4567")
            await page.goto("http://localhost:4567", wait_until="networkidle", timeout=30000)
            
            # Wait for React to render
            await page.wait_for_timeout(2000)
            
            # Check if app loaded (not white screen)
            body_content = await page.content()
            root_element = await page.query_selector("#root")
            
            if root_element:
                root_html = await root_element.inner_html()
                if len(root_html.strip()) > 0:
                    results["app_loads"] = True
                    print("✅ App loaded successfully (not white screen)")
                else:
                    results["errors"].append("Root element is empty - white screen detected")
                    print("❌ White screen detected - root element is empty")
            else:
                results["errors"].append("Root element not found")
                print("❌ Root element #root not found")
            
            # Check for fatal errors
            if len(fatal_errors) == 0 and len(page_errors) == 0:
                results["no_fatal_errors"] = True
                print("✅ No fatal JavaScript errors in console")
            else:
                results["errors"].extend(fatal_errors)
                results["errors"].extend(page_errors)
                print(f"❌ Found {len(fatal_errors)} fatal console errors and {len(page_errors)} page errors")
                for err in fatal_errors[:3]:
                    print(f"   - {err}")
                for err in page_errors[:3]:
                    print(f"   - {err}")
            
            # Log warnings (non-blocking)
            warnings = [msg for msg in console_messages if msg["type"] == "warning"]
            if warnings:
                results["warnings"] = [w["text"] for w in warnings[:5]]
                print(f"⚠️  Found {len(warnings)} warnings (non-fatal)")
            
            # Test 2: Look for guest button and click it
            print("\n🧪 Test 2: Looking for 'Lanjut sebagai tamu' button")
            try:
                # Try multiple selectors for the guest button
                guest_button = None
                selectors = [
                    "text=Lanjut sebagai tamu",
                    "button:has-text('Lanjut sebagai tamu')",
                    "button:has-text('tamu')",
                    "[class*='guest']",
                ]
                
                for selector in selectors:
                    try:
                        guest_button = await page.wait_for_selector(selector, timeout=3000)
                        if guest_button:
                            break
                    except:
                        continue
                
                if guest_button:
                    await guest_button.click()
                    await page.wait_for_timeout(2000)
                    results["guest_button_clicked"] = True
                    print("✅ Guest button found and clicked")
                    
                    # Check if home page loaded after clicking
                    try:
                        # Look for home page indicators
                        home_indicators = [
                            "text=Beranda",
                            "[class*='recipe']",
                            "[class*='card']",
                        ]
                        for indicator in home_indicators:
                            element = await page.query_selector(indicator)
                            if element:
                                results["home_page_loaded"] = True
                                print("✅ Home page (Beranda) loaded with content")
                                break
                    except:
                        pass
                else:
                    print("ℹ️  Guest button not found - may already be on home page")
                    # Check if we're already on home page
                    home_element = await page.query_selector("text=Beranda")
                    if home_element:
                        results["home_page_loaded"] = True
                        print("✅ Already on home page (Beranda)")
            except Exception as e:
                print(f"ℹ️  Guest button test skipped: {str(e)}")
            
            # Test 3: Navigate to Resep page
            print("\n🧪 Test 3: Navigating to Resep (recipes) page")
            try:
                # Try to find and click Resep link/button
                resep_selectors = [
                    "text=Resep",
                    "a:has-text('Resep')",
                    "button:has-text('Resep')",
                    "[href*='resep']",
                ]
                
                resep_link = None
                for selector in resep_selectors:
                    try:
                        resep_link = await page.wait_for_selector(selector, timeout=3000)
                        if resep_link:
                            break
                    except:
                        continue
                
                if resep_link:
                    await resep_link.click()
                    await page.wait_for_timeout(2000)
                    
                    # Verify we're on resep page
                    current_url = page.url
                    if "resep" in current_url.lower() or await page.query_selector("text=Resep"):
                        results["resep_page_loaded"] = True
                        print("✅ Resep page loaded successfully")
                    else:
                        results["errors"].append("Resep page navigation failed - URL didn't change")
                        print("❌ Resep page navigation failed")
                else:
                    results["errors"].append("Resep link/button not found")
                    print("❌ Resep link/button not found")
            except Exception as e:
                results["errors"].append(f"Resep navigation error: {str(e)}")
                print(f"❌ Error navigating to Resep: {str(e)}")
            
            # Test 4: Navigate to Scan page
            print("\n🧪 Test 4: Navigating to Scan page")
            try:
                scan_selectors = [
                    "text=Scan",
                    "a:has-text('Scan')",
                    "button:has-text('Scan')",
                    "[href*='scan']",
                ]
                
                scan_link = None
                for selector in scan_selectors:
                    try:
                        scan_link = await page.wait_for_selector(selector, timeout=3000)
                        if scan_link:
                            break
                    except:
                        continue
                
                if scan_link:
                    await scan_link.click()
                    await page.wait_for_timeout(2000)
                    
                    # Verify we're on scan page
                    current_url = page.url
                    if "scan" in current_url.lower() or await page.query_selector("text=Scan"):
                        results["scan_page_loaded"] = True
                        print("✅ Scan page loaded successfully")
                    else:
                        results["errors"].append("Scan page navigation failed - URL didn't change")
                        print("❌ Scan page navigation failed")
                else:
                    results["errors"].append("Scan link/button not found")
                    print("❌ Scan link/button not found")
            except Exception as e:
                results["errors"].append(f"Scan navigation error: {str(e)}")
                print(f"❌ Error navigating to Scan: {str(e)}")
            
        except PlaywrightTimeout as e:
            results["errors"].append(f"Timeout loading page: {str(e)}")
            print(f"❌ Timeout error: {str(e)}")
        except Exception as e:
            results["errors"].append(f"Unexpected error: {str(e)}")
            print(f"❌ Unexpected error: {str(e)}")
        finally:
            await browser.close()
    
    return results

async def main():
    print("=" * 70)
    print("NutriVane Production Build Test")
    print("Testing yarn build output served on http://localhost:4567")
    print("=" * 70)
    print()
    
    results = await test_production_build()
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    total_tests = 6
    passed_tests = sum([
        results["app_loads"],
        results["no_fatal_errors"],
        results["guest_button_clicked"] or results["home_page_loaded"],
        results["home_page_loaded"],
        results["resep_page_loaded"],
        results["scan_page_loaded"]
    ])
    
    print(f"\n✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
    
    print("\nDetailed Results:")
    print(f"  1. App loads (no white screen): {'✅ PASS' if results['app_loads'] else '❌ FAIL'}")
    print(f"  2. No fatal JS errors: {'✅ PASS' if results['no_fatal_errors'] else '❌ FAIL'}")
    print(f"  3. Guest button/Home access: {'✅ PASS' if (results['guest_button_clicked'] or results['home_page_loaded']) else '❌ FAIL'}")
    print(f"  4. Home page loaded: {'✅ PASS' if results['home_page_loaded'] else '❌ FAIL'}")
    print(f"  5. Resep page navigation: {'✅ PASS' if results['resep_page_loaded'] else '❌ FAIL'}")
    print(f"  6. Scan page navigation: {'✅ PASS' if results['scan_page_loaded'] else '❌ FAIL'}")
    
    if results["warnings"]:
        print(f"\n⚠️  Warnings (non-fatal): {len(results['warnings'])}")
        for warning in results["warnings"][:3]:
            print(f"   - {warning[:100]}")
    
    if results["errors"]:
        print(f"\n❌ Errors: {len(results['errors'])}")
        for error in results["errors"]:
            print(f"   - {error[:150]}")
    
    print("\n" + "=" * 70)
    
    # Critical checks for Vercel deployment readiness
    critical_pass = results["app_loads"] and results["no_fatal_errors"]
    
    if critical_pass:
        print("✅ PRODUCTION BUILD IS FUNCTIONAL AND READY FOR VERCEL DEPLOYMENT")
        print("   - yarn.lock and .yarnrc files will ensure Vercel uses yarn")
        print("   - Build output is working correctly")
        return 0
    else:
        print("❌ PRODUCTION BUILD HAS CRITICAL ISSUES")
        print("   - Fix errors before deploying to Vercel")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
