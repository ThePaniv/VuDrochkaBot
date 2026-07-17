output "deploy_role_arn" {
  description = "ARN hardcoded in .github/workflows/deploy.yml (DEPLOY_ROLE_ARN)."
  value       = aws_iam_role.deploy.arn
}

output "ecr_repository_url" {
  description = "Registry URI the workflow pushes to and the box pulls from."
  value       = aws_ecr_repository.bot.repository_url
}

output "lightsail_public_ip" {
  description = "Current public IP (also stored in the vudrochka-bot/deploy secret)."
  value       = aws_lightsail_instance.bot.public_ip_address
}

output "deploy_secret_arn" {
  description = "Secrets Manager secret holding the deploy target (value managed out-of-band)."
  value       = aws_secretsmanager_secret.deploy.arn
}
