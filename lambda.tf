module "source_lambda" {
  source        = "./source_data_lambda"
  source_s3_arn = aws_s3_bucket.data_source.arn
  prd           = "data-source"
  layers        = ["${aws_lambda_layer_version.layer.arn}"]
}

module "analytics_lambda" {
  source        = "./analytics_lambda"
  target_s3_arn = aws_s3_bucket.data_source.arn
  prd           = "analytics"
  layers        = ["${aws_lambda_layer_version.layer.arn}"]
  sqs_queue_arn = aws_sqs_queue.queue.arn
}

resource "aws_lambda_layer_version" "layer" {
  filename            = "python.zip"
  layer_name          = "Python3-pandas"
  source_code_hash    = filebase64sha256("python.zip")
  compatible_runtimes = ["python3.9"]
}
