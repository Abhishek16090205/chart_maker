import os
from minio import Minio
from minio.error import S3Error

MINIO_API = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

if not (MINIO_API and MINIO_ACCESS_KEY and MINIO_SECRET_KEY):
    raise RuntimeError(
        "Missing MinIO configuration. Please set MINIO_ENDPOINT, MINIO_ACCESS_KEY, and MINIO_SECRET_KEY environment variables."
    )

minio_client = Minio(
    MINIO_API,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)


def ensure_bucket(bucket_name: str) -> None:
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)


def get_object(bucket_name: str, object_name: str) -> bytes:
    try:
        response = minio_client.get_object(bucket_name, object_name)
        data = response.read()
        response.close()
        response.release_conn()
        return data
    except S3Error as e:
        raise Exception(f"Error getting object from MinIO: {str(e)}")


def put_object(bucket_name: str, object_name: str, file_path: str, content_type="text/csv"):
    try:
        ensure_bucket(bucket_name)
        minio_client.fput_object(bucket_name, object_name, file_path, content_type=content_type)
    except S3Error as e:
        raise Exception(f"Error putting object to MinIO: {str(e)}")

