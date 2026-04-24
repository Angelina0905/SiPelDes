import boto3
import os
import uuid

def upload_to_s3(file):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
            region_name=os.getenv('AWS_REGION')
        )

        bucket_name = os.getenv('AWS_BUCKET')

        filename = str(uuid.uuid4()) + "_" + file.filename

        s3.upload_fileobj(
            file,
            bucket_name,
            filename,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": file.content_type
            }
        )

        file_url = f"https://{bucket_name}.s3.amazonaws.com/{filename}"
        return file_url

    except Exception as e:
        print("S3 ERROR:", e)
        return None