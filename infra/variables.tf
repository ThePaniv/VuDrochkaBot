variable "aws_region" {
  description = "AWS region for all resources."
  type        = string
  default     = "eu-central-1"
}

variable "aws_profile" {
  description = "Local AWS CLI profile Terraform authenticates with (override for other machines/CI)."
  type        = string
  default     = "claude"
}

variable "github_repo" {
  description = "owner/repo whose Actions workflows may assume the deploy role via OIDC."
  type        = string
  default     = "ThePaniv/VuDrochkaBot"
}

variable "deploy_ref_branches" {
  description = "Branches whose OIDC token may assume the deploy role."
  type        = list(string)
  default     = ["deploy", "develop"]
}
