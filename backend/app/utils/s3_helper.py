import boto3
import os
import uuid
from werkzeug.utils import secure_filename

def upload_to_s3(file):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    bucket_name = os.getenv('S3_BUCKET')
    
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    try:
        s3_client.upload_fileobj(file, bucket_name, unique_filename, ExtraArgs={"ContentType": file.content_type})
        file_url = f"https://{bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{unique_filename}"
        return file_url
    except Exception as e:
        print("S3 Upload Error:", e)
        return None