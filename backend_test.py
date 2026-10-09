#!/usr/bin/env python3
"""
NutriVane Backend API Test Suite
Tests all backend endpoints for deployment readiness
"""
import requests
import json
import sys

# Backend URL - using localhost since we're testing internally
BASE_URL = "http://localhost:8001/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} - {name}")
    if details:
        print(f"  {details}")
    return passed

def test_health():
    """Test 1: Health endpoint - verifies Supabase Postgres connection"""
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        data = resp.json()
        passed = resp.status_code == 200 and data.get("ok") == True
        return print_test("GET /api/health", passed, 
                         f"Status: {resp.status_code}, Response: {data}")
    except Exception as e:
        return print_test("GET /api/health", False, f"Error: {str(e)}")

def test_recipes_list():
    """Test 2: Recipes list - should return 7 recipes"""
    try:
        resp = requests.get(f"{BASE_URL}/recipes", timeout=10)
        data = resp.json()
        passed = (resp.status_code == 200 and 
                 isinstance(data, list) and 
                 len(data) == 7 and
                 all(k in data[0] for k in ["slug", "name", "image", "source_count"]))
        details = f"Status: {resp.status_code}, Count: {len(data)}, Sample: {data[0]['name'] if data else 'N/A'}"
        return print_test("GET /api/recipes", passed, details)
    except Exception as e:
        return print_test("GET /api/recipes", False, f"Error: {str(e)}")

def test_home():
    """Test 3: Home endpoint - should return date, greeting, moods, picks"""
    try:
        resp = requests.get(f"{BASE_URL}/home", timeout=10)
        data = resp.json()
        required_keys = ["date", "part_of_day", "greeting_name", "moods", "picks"]
        passed = (resp.status_code == 200 and 
                 all(k in data for k in required_keys) and
                 isinstance(data["moods"], list) and
                 isinstance(data["picks"], list))
        details = f"Status: {resp.status_code}, Date: {data.get('date')}, Moods: {len(data.get('moods', []))}, Picks: {len(data.get('picks', []))}"
        return print_test("GET /api/home", passed, details)
    except Exception as e:
        return print_test("GET /api/home", False, f"Error: {str(e)}")

def test_recipe_detail():
    """Test 4: Recipe detail (rendang) - should return spices with pct fields"""
    try:
        resp = requests.get(f"{BASE_URL}/recipes/rendang", timeout=10)
        data = resp.json()
        passed = (resp.status_code == 200 and 
                 data.get("slug") == "rendang" and
                 "spices" in data and
                 isinstance(data["spices"], list) and
                 len(data["spices"]) > 0 and
                 "pct" in data["spices"][0] and
                 "sources" in data and
                 isinstance(data["sources"], list))
        details = f"Status: {resp.status_code}, Name: {data.get('name')}, Spices: {len(data.get('spices', []))}, Sources: {len(data.get('sources', []))}"
        return print_test("GET /api/recipes/rendang", passed, details)
    except Exception as e:
        return print_test("GET /api/recipes/rendang", False, f"Error: {str(e)}")

def test_scan_without_auth():
    """Test 5: POST /api/scan without auth - should work (optional auth)"""
    try:
        payload = {
            "benchmark_slug": "rendang",
            "measure": True
        }
        resp = requests.post(f"{BASE_URL}/scan", json=payload, timeout=15)
        data = resp.json()
        passed = (resp.status_code == 200 and 
                 data.get("benchmark_slug") == "rendang" and
                 data.get("menu_name") and
                 "spices" in data and
                 "insight" in data and
                 "vision_note" in data)
        details = f"Status: {resp.status_code}, Menu: {data.get('menu_name')}, Vision note: {data.get('vision_note', '')[:50]}..."
        return print_test("POST /api/scan (no auth)", passed, details)
    except Exception as e:
        return print_test("POST /api/scan (no auth)", False, f"Error: {str(e)}")

def test_categories():
    """Test 6: Categories endpoint - should return non-empty list"""
    try:
        resp = requests.get(f"{BASE_URL}/categories", timeout=10)
        data = resp.json()
        passed = (resp.status_code == 200 and 
                 isinstance(data, list) and 
                 len(data) > 0 and
                 all(k in data[0] for k in ["key", "label"]))
        details = f"Status: {resp.status_code}, Count: {len(data)}, Sample: {data[0] if data else 'N/A'}"
        return print_test("GET /api/categories", passed, details)
    except Exception as e:
        return print_test("GET /api/categories", False, f"Error: {str(e)}")

def test_moods():
    """Test 7: Moods endpoint - should return non-empty list"""
    try:
        resp = requests.get(f"{BASE_URL}/moods", timeout=10)
        data = resp.json()
        passed = (resp.status_code == 200 and 
                 isinstance(data, list) and 
                 len(data) > 0 and
                 all(k in data[0] for k in ["key", "label", "emoji"]))
        details = f"Status: {resp.status_code}, Count: {len(data)}, Sample: {data[0]['label'] if data else 'N/A'}"
        return print_test("GET /api/moods", passed, details)
    except Exception as e:
        return print_test("GET /api/moods", False, f"Error: {str(e)}")

def test_me_without_auth():
    """Test 8: GET /api/me without auth - should return 401"""
    try:
        resp = requests.get(f"{BASE_URL}/me", timeout=10)
        passed = resp.status_code == 401
        details = f"Status: {resp.status_code} (expected 401)"
        return print_test("GET /api/me (no auth, expect 401)", passed, details)
    except Exception as e:
        return print_test("GET /api/me (no auth, expect 401)", False, f"Error: {str(e)}")

def test_root():
    """Test 9: Root endpoint - basic connectivity"""
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=10)
        data = resp.json()
        passed = resp.status_code == 200 and data.get("app") == "NutriVane"
        return print_test("GET /api/", passed, f"Status: {resp.status_code}, Response: {data}")
    except Exception as e:
        return print_test("GET /api/", False, f"Error: {str(e)}")

def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}NutriVane Backend API Test Suite{Colors.END}")
    print(f"{Colors.BLUE}Testing: {BASE_URL}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    results = []
    
    # Run all tests
    results.append(test_root())
    results.append(test_health())
    results.append(test_recipes_list())
    results.append(test_home())
    results.append(test_recipe_detail())
    results.append(test_scan_without_auth())
    results.append(test_categories())
    results.append(test_moods())
    results.append(test_me_without_auth())
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    if passed == total:
        print(f"{Colors.GREEN}✓ ALL TESTS PASSED: {passed}/{total}{Colors.END}")
        print(f"{Colors.GREEN}Backend is deployment-ready!{Colors.END}")
    else:
        print(f"{Colors.RED}✗ SOME TESTS FAILED: {passed}/{total} passed{Colors.END}")
        print(f"{Colors.YELLOW}Review failed tests above{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
