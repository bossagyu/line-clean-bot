import boto3
from botocore.exceptions import ClientError


class S3client:
    def __init__(self, bucket_name):
        """Initiate S3client class
        :param bucket_name: bucket name
        """
        self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(bucket_name)

    def get_object_body(self, keyname):
        """Get object body from S3 bucket
        :param keyname: object key name
        :return: string of object body
        """
        object = self.bucket.Object(keyname)
        response = object.get()
        object_body = response['Body'].read().decode('utf-8')
        return object_body

    def list_objects(self):
        """List objects from S3 bucket
        :return: list of objects
        """
        objects = self.bucket.objects.all()
        return objects

    def check_exist_object(self, keyname):
        """Check if object exists in S3 bucket
        :param keyname: object key name
        :return: boolean
        """
        try:
            self.bucket.Object(keyname).load()
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print("Object does not exist.")
                return False
            else:
                print(f"An error occurred: {e}")
                raise e

    def delete_objects(self, objects):
        """Delete objects from S3 bucket
        :param objects: list of objects
        """
        objects.delete()

    def update_object(self, keyname, body):
        """Update object
        :param keyname: object key name
        :param body: object body
        """
        body = body.encode('utf-8')
        self.bucket.Object(keyname).put(Body=body)
