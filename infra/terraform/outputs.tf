output "ecr_repository_url" {
  value       = aws_ecr_repository.app.repository_url
  description = "ECR repository for the SLO alert lab image."
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.app.name
  description = "ECS cluster name for the deployment skeleton."
}
