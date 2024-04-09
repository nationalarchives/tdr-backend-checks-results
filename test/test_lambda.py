import pytest
from moto import mock_aws
import boto3
import json
from uuid import uuid4
from src.lambda_handler import lambda_handler

backend_checks_bucket = 'test-backend-checks-bucket'


@pytest.fixture(scope='function')
def s3():
    with mock_aws():
        yield boto3.client('s3', region_name='eu-west-2')


def setup_s3(s3):
    s3.create_bucket(Bucket=backend_checks_bucket,
                     CreateBucketConfiguration={
                         'LocationConstraint': 'eu-west-2'
                     })


def add_result_file(s3):
    outputs = json.dumps([
        {"Output": '{"test1": "value1"}'},
        {"Output": '{"test2": "value2"}'}
    ]).encode("utf-8")
    s3.put_object(Bucket=backend_checks_bucket, Key='test_key/succeeded.json', Body=outputs)


def add_manifest_file(s3):
    manifest_json = json.dumps(
        {
            "DestinationBucket": "test-backend-checks-bucket",
            "ResultFiles": {
                "SUCCEEDED": [
                    {
                        "Key": "test_key/succeeded.json",
                        "Size": 1
                    }
                ]
            }
        }
    ).encode("utf-8")
    key = f"{uuid4()}/{uuid4()}/results.json/{uuid4()}/manifest.json"
    s3.put_object(Bucket=backend_checks_bucket, Key=key, Body=manifest_json)
    return key


def get_event(key):
    return {
        "results": {
            "ResultWriterDetails": {
                "Bucket": backend_checks_bucket,
                "Key": key
            }
        }
    }


def get_result_json(s3, s3_event):
    obj_response = s3.get_object(Bucket=s3_event["bucket"], Key=s3_event["key"])["Body"]
    return json.loads(obj_response.read().decode("utf-8"))


def test_correct_result_is_stored(s3):
    setup_s3(s3)
    key = add_manifest_file(s3)
    add_result_file(s3)
    event = get_event(key)

    s3_event = lambda_handler(event, None)
    result_json = get_result_json(s3, s3_event)
    results = result_json["results"]
    assert results[0]["test1"] == "value1"
    assert results[1]["test2"] == "value2"
    assert result_json["statuses"]["statuses"] == []
    assert result_json["redactedResults"]["redactedFiles"] == []
    assert result_json["redactedResults"]["errors"] == []


def test_error_if_manifest_file_missing(s3):
    setup_s3(s3)
    add_result_file(s3)
    event = get_event("/key")

    with pytest.raises(Exception) as ex:
        lambda_handler(event, None)
    err_msg = 'An error occurred (NoSuchKey) when calling the GetObject operation: The specified key does not exist.'
    assert ex.value.args[0] == err_msg


def test_error_if_result_file_missing(s3):
    setup_s3(s3)
    add_manifest_file(s3)
    event = get_event("/key")

    with pytest.raises(Exception) as ex:
        lambda_handler(event, None)
    err_msg = 'An error occurred (NoSuchKey) when calling the GetObject operation: The specified key does not exist.'
    assert ex.value.args[0] == err_msg
