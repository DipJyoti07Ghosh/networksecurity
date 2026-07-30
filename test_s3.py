import os
import tempfile
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

# 1. Load environment variables from .env
load_dotenv()

bucket_name = os.getenv("S3_BUCKET_NAME")
region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

print("--- Starting S3 Connection & Permission Test ---")

# 2. Check if credentials are present in environment
if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
    print("❌ Error: AWS credentials missing in environment variables.")
    exit(1)

if not bucket_name:
    print("❌ Error: S3_BUCKET_NAME is not set in your .env file.")
    exit(1)

try:
    # 3. Initialize S3 client
    s3_client = boto3.client("s3", region_name=region)

    # 4. Test API authentication (Sts caller identity check)
    sts_client = boto3.client("sts", region_name=region)
    identity = sts_client.get_caller_identity()
    print(f"✅ AWS Credentials Validated! Authenticated as IAM Account/Role: {identity['Arn']}")

    # 5. Check if bucket exists & is accessible
    s3_client.head_bucket(Bucket=bucket_name)
    print(f"✅ Target S3 Bucket '{bucket_name}' exists and is accessible.")

    # 6. Test Write Permissions (Upload temporary file)
    test_key = "connection_test/test_file.txt"
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write("AWS S3 Connection Test - Successfully uploaded!")
        temp_file_path = temp_file.name

    s3_client.upload_file(temp_file_path, bucket_name, test_key)
    print(f"✅ UPLOAD SUCCESS: File uploaded to s3://{bucket_name}/{test_key}")

    # 7. Test Read Permissions (Download file)
    download_path = temp_file_path + "_downloaded"
    s3_client.download_file(bucket_name, test_key, download_path)
    print(f"✅ DOWNLOAD SUCCESS: Retrieved object back from S3.")

    # 8. Clean up test artifacts
    s3_client.delete_object(Bucket=bucket_name, Key=test_key)
    os.remove(temp_file_path)
    if os.path.exists(download_path):
        os.remove(download_path)
    print("✅ CLEANUP SUCCESS: Test object deleted from bucket.")

    print("\n🎉 ALL TESTS PASSED! Your S3 connection is ready for MLflow/Artifact logging.")

except NoCredentialsError:
    print("❌ ERROR: Could not locate AWS credentials.")
except ClientError as e:
    error_code = e.response.get("Error", {}).get("Code")
    if error_code == "403":
        print(f"❌ PERMISSION ERROR (403): Your IAM user does not have permission to access '{bucket_name}'. Check your S3 IAM policies.")
    elif error_code == "404":
        print(f"❌ NOT FOUND (404): The bucket '{bucket_name}' does not exist.")
    else:
        print(f"❌ AWS CLIENT ERROR: {e}")
except Exception as e:
    print(f"❌ UNEXPECTED ERROR: {e}")