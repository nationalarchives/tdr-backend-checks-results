import boto3
import json
import uuid


def lambda_handler(event, context):
    details = event["results"]["ResultWriterDetails"]
    bucket = details["Bucket"]
    manifest_key = details["Key"]
    consignment_id = manifest_key.split("/")[0]

    s3 = boto3.client("s3")
    s3_response_object = s3.get_object(Bucket=bucket, Key=manifest_key)
    object_content = s3_response_object['Body'].read()
    response = json.loads(object_content.decode("utf-8"))

    success = response["ResultFiles"]["SUCCEEDED"][0]
    results_json_key = success["Key"]

    map_output = json.loads(s3.get_object(Bucket=bucket, Key=results_json_key)["Body"].read().decode("utf-8"))
    res = {
        "results": [json.loads(result["Output"]) for result in map_output],
        "statuses": {
            "statuses": []
        },
        "redactedResults": {
            "redactedFiles": [],
            "errors": []
        }
    }
    results_key = f"{consignment_id}/{uuid.uuid4()}/results.json"
    bucket = bucket

    s3.put_object(
        Body=json.dumps(res),
        Bucket=bucket,
        Key=results_key,
    )
    return {
        "key": results_key,
        "bucket": bucket
    }
