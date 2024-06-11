output "endpoint_url" {
  value = "${aws_api_gateway_stage.example.invoke_url}/${var.endpoint_path}?search_term=Python&kinesis_stream=test_stream&from_date=2024-01-01"
}