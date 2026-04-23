import boto3, os, uuid
from werkzeug.utils import secure_filename

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='ap-southeast-1'
)
BUCKET = os.getenv('S3_BUCKET', 'sipledes-files')

def upload_file(file_obj, folder='uploads'):
    filename = f"{folder}/{uuid.uuid4()}_{secure_filename(file_obj.filename)}"
    s3.upload_fileobj(file_obj, BUCKET, filename, ExtraArgs={'ACL': 'private'})
    url = f"https://{BUCKET}.s3.amazonaws.com/{filename}"
    return url