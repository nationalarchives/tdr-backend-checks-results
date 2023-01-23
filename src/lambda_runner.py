from src.lambda_handler import lambda_handler

event = {
  "results": {
    "ResultWriterDetails": {
      "Bucket": "tdr-backend-checks-intg",
      "Key": "{consignment_id}/{random_uuid}/results.json/{sfn_generated_id}/manifest.json"
    }
  }
}
lambda_handler(event, None)
