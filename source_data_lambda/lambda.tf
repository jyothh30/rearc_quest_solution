data "archive_file" "zip" {
  type        = "zip"
  source_file = "source_data_lambda/src/main.py"
  output_path = "source_data_lambda/src/main.zip"
}

# Todo: Pass s3 arn in environment 
resource "aws_lambda_function" "lambda" {
  function_name    = "${var.prd}-lambda"
  description      = "${var.prd} Lambda Function"
  handler          = "main.lambda_handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda-role.arn
  filename         = "source_data_lambda/src/main.zip"
  source_code_hash = data.archive_file.zip.output_base64sha256
  layers           = var.layers

  environment {
    variables = {
      BUCKET_ARN = "${var.source_s3_arn}"
    }
  }
}