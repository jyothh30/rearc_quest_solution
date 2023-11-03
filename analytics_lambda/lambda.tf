
data "archive_file" "zip" {
  type        = "zip"
  source_file = "analytics_lambda/src/handler.py"
  output_path = "analytics_lambda/src/handler.zip"
}

resource "aws_lambda_function" "lambda" {
  function_name    = "${var.prd}-lambda"
  description      = "Analytics Lambda Function"
  handler          = "main.lambda_handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda-role.arn
  filename         = "analytics_lambda/src/handler.zip"
  source_code_hash = data.archive_file.zip.output_base64sha256
  layers           = var.layers
  environment {
    variables = {
      BUCKET_ARN = "${var.target_s3_arn}"
    }
  }
}

#Lambda SQS Trigger
resource "aws_lambda_event_source_mapping" "lambda_test_sqs_trigger" {
  event_source_arn = var.sqs_queue_arn
  function_name    = aws_lambda_function.lambda.arn
}