"""Safe, minimal live connectivity test for Amazon Bedrock Converse API with Nova 2 Lite."""
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError


def run_live_connectivity_test():
    region = os.getenv("AWS_REGION", "us-east-1").strip()
    model_id = os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-2-lite-v1:0").strip()

    print("\n" + "=" * 60)
    print("AMAZON BEDROCK LIVE CONNECTIVITY TEST")
    print("=" * 60)
    print(f"Target AWS Region:        {region}")
    print(f"Target Inference Profile: {model_id}")

    # 1. Check credentials
    session = boto3.Session(region_name=region)
    credentials = session.get_credentials()
    
    if not credentials:
        print("\n[FAIL] No AWS credentials discovered in the credential chain.")
        print("Please ensure your AWS CLI is authenticated (e.g. via 'aws login' or ~/.aws/credentials).")
        return False

    # Get credential method without printing secrets
    method = getattr(credentials, "method", "standard")
    print(f"AWS Credentials Source:   Found (via '{method}')")

    # 2. Initialize bedrock-runtime client
    retry_config = Config(
        region_name=region,
        retries={"max_attempts": 2, "mode": "standard"},
        connect_timeout=10,
        read_timeout=30,
    )
    
    try:
        client = session.client("bedrock-runtime", config=retry_config)
    except Exception as e:
        print(f"\n[FAIL] Failed to create Bedrock Runtime client: {e}")
        return False

    # 3. Perform a minimal, cost-conscious Converse API invocation
    print("\nInvoking Amazon Bedrock Converse API...")
    start_time = time.time()

    try:
        response = client.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "Hello Nova! Reply with a JSON object: {\"status\": \"active\", \"service\": \"JobLens AI\"}"
                        }
                    ],
                }
            ],
            inferenceConfig={
                "temperature": 0.1,
                "maxTokens": 100,
            },
        )
        latency = time.time() - start_time

        # Extract output
        output_message = response.get("output", {}).get("message", {})
        content_list = output_message.get("content", [])
        response_text = content_list[0].get("text", "").strip() if content_list else "No text returned"
        usage = response.get("usage", {})

        print("\n" + "-" * 60)
        print("BEDROCK CONVERSE API CALL SUCCEEDED! [OK]")
        print("-" * 60)
        print(f"Latency:         {latency:.2f} seconds")
        print(f"Input Tokens:    {usage.get('inputTokens', 'N/A')}")
        print(f"Output Tokens:   {usage.get('outputTokens', 'N/A')}")
        print(f"Model Response:  {response_text}")
        print("=" * 60 + "\n")
        return True

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_msg = e.response.get("Error", {}).get("Message", str(e))
        print(f"\n[FAIL] Bedrock ClientError [{error_code}]: {error_msg}")
        return False
    except (NoCredentialsError, EndpointConnectionError) as e:
        print(f"\n[FAIL] Connection / Credential Error: {e}")
        return False
    except Exception as e:
        print(f"\n[FAIL] Unexpected Error: {e}")
        return False


if __name__ == "__main__":
    success = run_live_connectivity_test()
    sys.exit(0 if success else 1)
