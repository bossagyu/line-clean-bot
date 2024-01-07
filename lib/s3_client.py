import boto3


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

    def delete_objects(self, objects):
        """Delete objects from S3 bucket
        :param objects: list of objects
        """
        objects.delete()
