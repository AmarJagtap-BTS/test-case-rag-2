#!/usr/bin/env python3
"""
Network and Azure OpenAI connectivity diagnostic
"""
import subprocess
import socket
import time
from config import Config

def run_command(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=10
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)

def test_dns_resolution():
    """Test if endpoint can be resolved"""
    print("\n" + "="*80)
    print("TEST 1: DNS Resolution")
    print("="*80)
    
    endpoint = Config.AZURE_OPENAI_ENDPOINT.replace("https://", "").replace("/", "")
    print(f"Resolving: {endpoint}")
    
    try:
        ip_address = socket.gethostbyname(endpoint)
        print(f"✓ Resolved to: {ip_address}")
        return True
    except socket.gaierror as e:
        print(f"✗ DNS resolution failed: {e}")
        print("  → Check internet connection")
        print("  → Check VPN status")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_internet_connectivity():
    """Test basic internet connectivity"""
    print("\n" + "="*80)
    print("TEST 2: Internet Connectivity")
    print("="*80)
    
    test_hosts = [
        ("google.com", "Google"),
        ("azure.com", "Azure"),
        ("microsoft.com", "Microsoft")
    ]
    
    all_ok = True
    for host, name in test_hosts:
        try:
            socket.create_connection((host, 80), timeout=5)
            print(f"✓ Can reach {name} ({host})")
        except Exception as e:
            print(f"✗ Cannot reach {name} ({host}): {e}")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️ Internet connectivity issues detected")
        print("  → Check your network connection")
        print("  → Verify Wi-Fi/Ethernet is connected")
    
    return all_ok

def test_endpoint_connectivity():
    """Test HTTP connectivity to Azure OpenAI endpoint"""
    print("\n" + "="*80)
    print("TEST 3: Azure OpenAI Endpoint Connectivity")
    print("="*80)
    
    endpoint = Config.AZURE_OPENAI_ENDPOINT
    print(f"Testing: {endpoint}")
    
    # Try curl
    code, stdout, stderr = run_command(f"curl -s -I {endpoint} --max-time 10")
    
    if code == 0 and "200" in stdout:
        print("✓ Endpoint is reachable via HTTP")
        return True
    elif code == 6:
        print("✗ Could not resolve host (DNS issue)")
        return False
    elif code == 7:
        print("✗ Failed to connect to host (Network/Firewall issue)")
        return False
    elif code == 28:
        print("✗ Connection timeout (Network slow/Firewall)")
        return False
    else:
        print(f"✗ Connection failed (code: {code})")
        if stderr:
            print(f"  Error: {stderr}")
        return False

def test_vpn_requirement():
    """Check if VPN might be required"""
    print("\n" + "="*80)
    print("TEST 4: VPN Requirement Check")
    print("="*80)
    
    # Check if we can reach Azure but not the specific endpoint
    try:
        socket.create_connection(("azure.com", 443), timeout=5)
        azure_reachable = True
    except:
        azure_reachable = False
    
    endpoint = Config.AZURE_OPENAI_ENDPOINT.replace("https://", "").replace("/", "")
    try:
        socket.create_connection((endpoint, 443), timeout=5)
        endpoint_reachable = True
    except:
        endpoint_reachable = False
    
    if azure_reachable and not endpoint_reachable:
        print("⚠️ Azure is reachable but your endpoint is not")
        print("  → This often indicates VPN is required")
        print("  → Your Azure OpenAI resource may be in a private network")
        print("  → Contact your Azure admin")
        return False
    elif not azure_reachable:
        print("⚠️ Cannot reach Azure at all")
        print("  → Check internet connection")
        print("  → Verify firewall settings")
        return False
    else:
        print("✓ Both Azure and endpoint are reachable")
        return True

def test_azure_openai_api():
    """Quick API test"""
    print("\n" + "="*80)
    print("TEST 5: Azure OpenAI API Test")
    print("="*80)
    
    try:
        from openai import AzureOpenAI
        
        print("Creating client...")
        client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            timeout=10.0,
            max_retries=1
        )
        
        print("Testing simple completion...")
        response = client.chat.completions.create(
            model=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=5
        )
        
        print(f"✓ API test successful!")
        print(f"  Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"✗ API test failed: {error_msg}")
        
        if "connection" in error_msg.lower():
            print("  → Network/Firewall issue")
        elif "401" in error_msg:
            print("  → Invalid API key")
        elif "404" in error_msg:
            print("  → Deployment not found")
        else:
            print(f"  → Error: {error_msg[:100]}")
        
        return False

def main():
    """Run all diagnostic tests"""
    print("="*80)
    print("NETWORK & AZURE OPENAI CONNECTIVITY DIAGNOSTIC")
    print("="*80)
    print(f"Endpoint: {Config.AZURE_OPENAI_ENDPOINT}")
    print(f"Deployment: {Config.AZURE_OPENAI_DEPLOYMENT_NAME}")
    
    results = {
        "DNS Resolution": test_dns_resolution(),
        "Internet": test_internet_connectivity(),
        "Endpoint": test_endpoint_connectivity(),
        "VPN": test_vpn_requirement(),
        "API": test_azure_openai_api()
    }
    
    print("\n" + "="*80)
    print("DIAGNOSTIC SUMMARY")
    print("="*80)
    
    for test, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test:20} {status}")
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    if not results["DNS Resolution"]:
        print("🔴 CRITICAL: DNS resolution failed")
        print("   1. Check internet connection")
        print("   2. Verify network settings")
        print("   3. Try: ping google.com")
    
    elif not results["Internet"]:
        print("🔴 CRITICAL: Internet connectivity issues")
        print("   1. Check Wi-Fi/Ethernet connection")
        print("   2. Restart router if needed")
        print("   3. Contact IT support")
    
    elif not results["Endpoint"]:
        print("🟡 WARNING: Endpoint unreachable")
        print("   1. Check if VPN is required")
        print("   2. Verify firewall settings")
        print("   3. Contact Azure administrator")
        print("   4. Wait and retry (may be temporary)")
    
    elif not results["API"]:
        print("🟡 WARNING: API call failed")
        print("   1. Verify API key in Azure Portal")
        print("   2. Check deployment name")
        print("   3. Verify quota/limits")
    
    else:
        print("✅ ALL TESTS PASSED!")
        print("   Your connection to Azure OpenAI is working")
        print("   If you're still seeing errors, try:")
        print("   1. Restart Streamlit")
        print("   2. Clear browser cache")
        print("   3. Click button only once")

if __name__ == "__main__":
    main()
