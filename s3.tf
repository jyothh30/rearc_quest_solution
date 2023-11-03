resource "random_string" "random" {
  length           = 8
  special          = false
  override_special = "/@£$"
  lower            = true
  upper            = false
}

resource "aws_s3_bucket" "data_source" {
  bucket = "${var.bucket_name_prefix}-${random_string.random.result}"

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}

resource "aws_s3_bucket_policy" "allow_public_access" {
  bucket = aws_s3_bucket.data_source.id
  policy = data.aws_iam_policy_document.allow_public_access.json
}

resource "aws_s3_bucket_public_access_block" "example" {
  bucket = aws_s3_bucket.data_source.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

data "aws_iam_policy_document" "allow_public_access" {
  statement {
    sid    = "Stmt1698942379656"
    effect = "Allow"
    resources = [
      aws_s3_bucket.data_source.arn,
      "${aws_s3_bucket.data_source.arn}/*",
    ]

    actions = [
      "s3:GetObject",
      "s3:GetObjectTagging",
      "s3:GetObjectVersion",
      "s3:GetObjectVersionAttributes",
      "s3:GetObjectVersionTagging",
      "s3:ListBucket",
      "s3:ListBucketVersions",
      "s3:PutBucketPolicy",
      "s3:DeleteObject",
    ]

    principals {
      type        = "*"
      identifiers = ["*"]
    }
  }
}


resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.data_source.id
  queue {
    queue_arn     = aws_sqs_queue.queue.arn
    events        = ["s3:ObjectCreated:*"]
    filter_suffix = ".json"
    filter_prefix = "API/"
  }
}