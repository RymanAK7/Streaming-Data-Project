variable "myregion" {
  description = "The AWS region"
  type        = string
  default     = "eu-west-2"
}

variable "accountId" {
  description = "The AWS account ID"
  type        = string
}

variable "lambda_function_name" {
  description = "What to name the lambda function"
  type        = string
  default     = "articles_to_kinesis"
}

variable "endpoint_path" {
  description = "The GET endpoint path"
  type        = string
  default     = "publish"
}

variable "kinesis_stream_name" {
  description = "Name of kinesis stream"
  type        = string
}