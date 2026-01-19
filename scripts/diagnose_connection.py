"""
Detailed Azure OpenAI connection diagnostic
"""
from openai import AzureOpenAI
from config import Config
import traceback

def test_connection_detailed():
    """Test Azure OpenAI connection with detailed diagnostics"""
    
    print("=" * 80)
    print("AZURE OPENAI CONNECTION DIAGNOSTIC")
    print("=" * 80)
    
    print("\n📋 Current Configuration:")
    print(f"  Endpoint: {Config.AZURE_OPENAI_ENDPOINT}")
    print(f"  API Version: {Config.AZURE_OPENAI_API_VERSION}")
    print(f"  Deployment: {Config.AZURE_OPENAI_DEPLOYMENT_NAME}")
    print(f"  Embedding Deployment: {Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}")
    print(f"  API Key: {Config.AZURE_OPENAI_API_KEY[:20]}...{Config.AZURE_OPENAI_API_KEY[-10:]}")
    
    # Test 1: Create client
    print("\n" + "=" * 80)
    print("TEST 1: Creating Azure OpenAI Client")
    print("=" * 80)
    
    try:
        client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            timeout=30.0,
            max_retries=1
        )
        print("✓ Client created successfully")
    except Exception as e:
        print(f"✗ Failed to create client: {e}")
        traceback.print_exc()
        return False
    
    # Test 2: Try different API versions
    print("\n" + "=" * 80)
    print("TEST 2: Testing Different API Versions")
    print("=" * 80)
    
    api_versions = [
        "2024-08-01-preview",
        "2024-06-01",
        "2024-05-01-preview",
        "2024-02-15-preview",
        "2023-12-01-preview"
    ]
    
    for version in api_versions:
        try:
            print(f"\nTrying API version: {version}")
            test_client = AzureOpenAI(
                api_key=Config.AZURE_OPENAI_API_KEY,
                api_version=version,
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                timeout=10.0,
                max_retries=0
            )
            
            # Try a simple completion
            response = test_client.chat.completions.create(
                model=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            print(f"  ✓ SUCCESS with {version}")
            print(f"  Response: {response.choices[0].message.content}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                print(f"  ✗ Deployment not found with {version}")
            elif "401" in error_msg:
                print(f"  ✗ Authentication failed with {version}")
            elif "connection" in error_msg.lower():
                print(f"  ✗ Connection error with {version}")
            else:
                print(f"  ✗ Error with {version}: {error_msg[:100]}")
    
    # Test 3: Try different deployment names
    print("\n" + "=" * 80)
    print("TEST 3: Testing Common Deployment Names")
    print("=" * 80)
    
    deployment_names = [
        Config.AZURE_OPENAI_DEPLOYMENT_NAME,
        "gpt-4",
        "gpt-4-turbo",
        "gpt-35-turbo",
        "gpt-4o",
        "gpt-4o-mini"
    ]
    
    for deployment in deployment_names:
        try:
            print(f"\nTrying deployment: {deployment}")
            test_client = AzureOpenAI(
                api_key=Config.AZURE_OPENAI_API_KEY,
                api_version="2024-02-15-preview",
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                timeout=10.0,
                max_retries=0
            )
            
            response = test_client.chat.completions.create(
                model=deployment,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            print(f"  ✓ SUCCESS with deployment: {deployment}")
            print(f"  Response: {response.choices[0].message.content}")
            
            # Update config suggestion
            print(f"\n  💡 SOLUTION FOUND!")
            print(f"     Update config.py to use deployment: '{deployment}'")
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "DeploymentNotFound" in error_msg:
                print(f"  ✗ Deployment '{deployment}' not found")
            elif "401" in error_msg:
                print(f"  ✗ Authentication failed")
            elif "connection" in error_msg.lower():
                print(f"  ✗ Connection error")
            else:
                print(f"  ✗ Error: {error_msg[:80]}")
    
    # Test 4: Test embedding endpoint
    print("\n" + "=" * 80)
    print("TEST 4: Testing Embedding Endpoint")
    print("=" * 80)
    
    try:
        print(f"Trying embedding deployment: {Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}")
        client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version="2024-02-15-preview",
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            timeout=10.0
        )
        
        response = client.embeddings.create(
            model=Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            input="test"
        )
        print(f"  ✓ Embedding endpoint works!")
        print(f"  Embedding dimensions: {len(response.data[0].embedding)}")
        
    except Exception as e:
        print(f"  ✗ Embedding failed: {e}")
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    
    print("\n🔍 NEXT STEPS:")
    print("1. Check if the API key is still valid in Azure Portal")
    print("2. Verify the deployment name in Azure OpenAI Studio")
    print("3. Check if you're connected to the correct network/VPN")
    print("4. Contact Azure admin to verify resource access")
    
    return False

if __name__ == "__main__":
    test_connection_detailed()
