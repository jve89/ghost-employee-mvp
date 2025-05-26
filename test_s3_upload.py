import boto3
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client('s3')
s3.put_object(Bucket='my-ghost-employee-exports', Key='test.txt', Body=b'hello world')
print("Upload successful")
