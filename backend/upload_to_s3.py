import boto3
import os
import uuid

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

def upload_to_s3(file):
    try:
        bucket_name = os.getenv("AWS_BUCKET_NAME")

        # bikin nama file unik
        filename = str(uuid.uuid4()) + "_" + file.filename

        s3.upload_fileobj(
            file,
            bucket_name,
            filename,
            ExtraArgs={
                "ACL": "public-read",   # 🔥 biar bisa diakses link
                "ContentType": file.content_type
            }
        )

        # URL file
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{filename}"
        return file_url

    except Exception as e:
        print("ERROR S3:", e)
        return None