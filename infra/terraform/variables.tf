variable "region" {
  type        = string
  description = "AWS region for the ECS skeleton."
  default     = "us-west-2"
}

variable "service_name" {
  type        = string
  description = "Service name used for container infrastructure."
  default     = "prometheus-slo-alert-lab"
}

variable "image_uri" {
  type        = string
  description = "Container image URI to deploy."
  default     = "example/prometheus-slo-alert-lab:latest"
}

variable "ecs_task_execution_role_arn" {
  type        = string
  description = "Existing ECS task execution role ARN."
  default     = "arn:aws:iam::123456789012:role/ecsTaskExecutionRole"
}
