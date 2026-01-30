import boto3
import pytest
from moto import mock_aws

from lib.s3_client import S3client


@pytest.fixture
def aws_credentials():
    """AWS Credentials for moto."""
    boto3.setup_default_session(aws_access_key_id="testing", aws_secret_access_key="testing",
                                aws_session_token="testing")


@pytest.fixture
def s3_client(aws_credentials):
    with mock_aws():
        yield boto3.client('s3', region_name='us-east-1')


@pytest.fixture
def s3_setup(s3_client):
    bucket_name = "test-bucket"
    s3_client.create_bucket(Bucket=bucket_name)
    return bucket_name


def test_list_objects(s3_setup):
    bucket_name = s3_setup
    client = S3client(bucket_name)
    s3 = boto3.resource('s3')
    s3.Object(bucket_name, "test.txt").put(Body="This is a test file")

    objects = client.list_objects()
    object_keys = [obj.key for obj in objects]

    assert "test.txt" in object_keys


def test_get_object_body(s3_setup):
    bucket_name = s3_setup
    client = S3client(bucket_name)
    s3 = boto3.resource('s3')
    test_body = "Hello World"
    s3.Object(bucket_name, "hello.txt").put(Body=test_body)

    body = client.get_object_body("hello.txt")

    assert body == test_body


def test_check_exist_object(s3_setup):
    bucket_name = s3_setup
    client = S3client(bucket_name)
    s3 = boto3.resource('s3')
    s3.Object(bucket_name, "exist.txt").put(Body="This is a test file")

    assert client.check_exist_object("exist.txt") is True
    assert client.check_exist_object("not_exist.txt") is False


def test_delete_objects(s3_setup):
    bucket_name = s3_setup
    client = S3client(bucket_name)
    s3 = boto3.resource('s3')
    s3.Object(bucket_name, "delete_me.txt").put(Body="Delete this file")

    objects = client.list_objects()
    client.delete_objects(objects)

    objects_after_delete = list(client.list_objects())
    assert len(objects_after_delete) == 0

