variable "source_s3_arn" {
  type        = string
  description = "ARN of S3 bucket where the Source data is stored"
}

variable "prd" {
  type        = string
  description = "unique identifier tag"
}
variable "layers" {
  type        = list(string)
  description = "lambda layer"
}