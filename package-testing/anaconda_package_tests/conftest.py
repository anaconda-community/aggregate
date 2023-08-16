import logging

# import os
# import time
#
# import boto3

logging_level = logging.INFO
logging.basicConfig(level=logging_level)


def pytest_addoption(parser):
    parser.addoption("--package_name", action="store", default="", help="Package to be tested")
    parser.addoption(
        "--project_name",
        action="store",
        default="Packaging Team Integration Tests",
        help=" Project name",
    )


# def pytest_sessionfinish(session, exitstatus):
#     """
#     executes after whole test run finishes.
#     calling
#     """
#     date = time.strftime("%Y-%m-%d_%H:%M:%S")
#     artifact_path = os.environ.get("ARTIFACTS_PATH", "")
#     print("file path", artifact_path)
#     out_put_file = f"{artifact_path}/test-report.html"
#     s3_bucket = os.environ.get("S3_BUCKET")
#     s3_client = boto3.client(
#         "s3",
#         aws_access_key_id=os.environ.get("AWS_S3_ACCESS_KEY"),
#         aws_secret_access_key=os.environ.get("AWS_S3_SECRET_KEY"),
#     )
#     logging.log(
#         logging_level,
#         f"Uploading test report to s3 bucket \
#     {out_put_file} to {s3_bucket}.",
#     )
#     obj_name = f"/packages/{date}/test-report.html"
#     s3_client.put_object(Body=out_put_file, Bucket=s3_bucket, Key=obj_name)
#     logging.log(
#         logging_level,
#         f"Uploaded test report {out_put_file} \
#     to {s3_bucket} as {obj_name}.",
#     )
