# TDR Backend Checks Results

The map step inside the backend checks step function reads its input from S3 and writes its output back to S3.

Instead  of configuring each of the backend checks to read and write their own updates to S3, we're making use of a feature of the step functions which writes the outut to S3.

The format cannot be changed so this lambda aggregates all the results and writes them back to S3 in a format useable by the next lambdas in the chain.

The message from the map function has this format:

```json
{
  "results": {
    "ResultWriterDetails": {
      "Bucket": "tdr-backend-checks-intg",
      "Key": "{consignment_id}/{random_uuid}/results.json/{sfn_generated_id}/manifest.json"
    }
  }
}
```
This lambda gets the `{consignment_id}/{random_uuid}/results.json/{sfn_generated_id}/manifest.json` key from the `tdr-backend-checks-intg` bucket.

This file has the following format:
```json
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
```
If any of the files fail, the step function catches the error and bypasses this lambda. We should only get SUCCESS states.

The lambda then gets the file at `test_key/succeeded.json`. This has the format:

```json
[
        {"Output": "{\"test1\": \"value1\"}"},
        {"Output": "{\"test2\": \"value2\"}"}
    ]
```
Each of these json strings are parsed and added to a `results` key and this json object is stored in S3. 
The key is in the form `{consignment_id}/{random_uuid}/results.json` The bucket and the key are returned in the output from the lambda.

## Running the code
There is a lambda_handler.py file which can be run to test the lambda locally. The files mentioned above will all need to exist in the correct format and you'll need credentials to access the files in S3.

## Running the tests
Run the tests with a virtual environment and pytest.
```commandline
python -m venv venv
source venv/bin/activate
python -m pytest
```
