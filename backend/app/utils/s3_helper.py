import boto3
import os
import uuid
from werkzeug.utils import secure_filename

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'ap-southeast-2')
BUCKET = os.getenv('S3_BUCKET', 'sipeldes-bucket')

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def upload_file(file_obj, folder='surat'):
    try:
        filename = f"{folder}/{uuid.uuid4()}_{secure_filename(file_obj.filename)}"

        s3.upload_fileobj(file_obj, BUCKET, filename)

        url = f"https://{BUCKET}.s3.{AWS_REGION}.amazonaws.com/{filename}"

        print("Upload berhasil:", url)
        return url

    except Exception as e:
        print("Upload gagal:", str(e))
        return None