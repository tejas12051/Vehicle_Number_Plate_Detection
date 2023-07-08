import boto3
import os


class S3Client:

    s3_client=None
    s3_resource = None
    def __init__(self, region_name=os.environ["AWS_DEFAULT_REGION"]):

        if S3Client.s3_resource==None or S3Client.s3_client==None:
            __access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
            __secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]
            if __access_key_id is None:
                raise Exception("Environment variable:  is not not set.")
            if __secret_access_key is None:
                raise Exception("Environment variable:  is not set.")
        
            S3Client.s3_resource = boto3.resource('s3',
                                            aws_access_key_id=__access_key_id,
                                            aws_secret_access_key=__secret_access_key,
                                            region_name=region_name
                                            )
            S3Client.s3_client = boto3.client('s3',
                                        aws_access_key_id=__access_key_id,
                                        aws_secret_access_key=__secret_access_key,
                                        region_name=region_name
                                        )
        self.s3_resource = S3Client.s3_resource
        self.s3_client = S3Client.s3_client