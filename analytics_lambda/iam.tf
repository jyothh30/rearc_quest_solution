resource "aws_iam_role" "lambda-role" {
  name               = "${var.prd}-lambda-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": "1"
    }
  ]
}
EOF
}

data "aws_iam_policy_document" "lambda-policy-doc" {
  statement {
    sid    = "AllowCreatingLogGroups"
    effect = "Allow"

    resources = [
      "arn:aws:logs:*:*:*"
    ]

    actions = [
      "logs:CreateLogGroup"
    ]
  }
  statement {
    sid    = "AllowWritingLogs"
    effect = "Allow"

    resources = [
      "arn:aws:logs:*:*:log-group:/aws/lambda/*:*"
    ]

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
  }
  statement {
    sid    = "AllowS3"
    effect = "Allow"

    resources = [
      var.target_s3_arn,
      "${var.target_s3_arn}/*"
    ]

    actions = [
      "s3:Put*",
      "s3:Get*"
    ]
  }
}

resource "aws_iam_policy" "lambda-policy" {
  name   = "${var.prd}-lambda-policy"
  policy = data.aws_iam_policy_document.lambda-policy-doc.json
}

resource "aws_iam_role_policy_attachment" "lambda-role" {
  policy_arn = aws_iam_policy.lambda-policy.arn
  role       = aws_iam_role.lambda-role.name
}

#Attachment of a Managed AWS IAM Policy for Lambda sqs execution
resource "aws_iam_role_policy_attachment" "lambda_basic_sqs_queue_execution_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"
  role       = aws_iam_role.lambda-role.name
}
