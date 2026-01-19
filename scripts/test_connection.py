"""
Test script to verify Azure OpenAI connection
"""
from openai import AzureOpenAI
from config import Config

def test_connection():
    """Test Azure OpenAI connection"""
    print("Testing Azure OpenAI connection...")
    print(f"Endpoint: {Config.AZURE_OPENAI_ENDPOINT}")
    print(f"API Version: {Config.AZURE_OPENAI_API_VERSION}")
    print(f"Deployment: {Config.AZURE_OPENAI_DEPLOYMENT_NAME}")
    print(f"Embedding Deployment: {Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}")
    
    try:
        client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            timeout=30.0,
            max_retries=2
        )
        
        # Test chat completion
        print("\n1. Testing chat completion...")
        response = client.chat.completions.create(
            model=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "user", "content": "Say 'Connection successful!'"}
            ],
            max_tokens=50
        )
        print(f"✓ Chat completion successful: {response.choices[0].message.content}")
        
        # Test embedding
        print("\n2. Testing embeddings...")
        response = client.embeddings.create(
            model=Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            input="test"
        )
        print(f"✓ Embedding successful: {len(response.data[0].embedding)} dimensions")
        
        print("\n✓✓ All tests passed! Connection is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n✗ Connection failed!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")
        
        # Print troubleshooting tips
        print("\n=== Troubleshooting Tips ===")
        if "404" in str(e):
            print("• The deployment name might be incorrect")
            print("• Check that your deployment exists in Azure OpenAI portal")
        elif "401" in str(e) or "authentication" in str(e).lower():
            print("• API key might be invalid or expired")
            print("• Verify your API key in Azure Portal")
        elif "timeout" in str(e).lower():
            print("• Connection timed out")
            print("• Check your network connection")
            print("• Verify firewall settings")
        elif "connection" in str(e).lower():
            print("• Cannot connect to endpoint")
            print("• Verify the endpoint URL")
            print("• Check network/VPN connection")
        else:
            print("• Check all configuration values")
            print("• Verify resource exists in Azure")
        
        return False

if __name__ == "__main__":
    test_connection()
