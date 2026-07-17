# One-time import wiring (Terraform >= 1.5): brings the resources — originally
# created via the AWS CLI — under Terraform management WITHOUT recreating them.
# `terraform plan` should report "N to import, 0 to add, 0 to change, 0 to
# destroy". These blocks are no-ops after the import and safe to leave.

import {
  to = aws_iam_openid_connect_provider.github
  id = "arn:aws:iam::126568927381:oidc-provider/token.actions.githubusercontent.com"
}

import {
  to = aws_iam_role.deploy
  id = "github-actions-vudrochka-deploy"
}

import {
  to = aws_iam_role_policy.ecr_push
  id = "github-actions-vudrochka-deploy:ecr-push"
}

import {
  to = aws_iam_role_policy.secrets_read
  id = "github-actions-vudrochka-deploy:secrets-read"
}

import {
  to = aws_ecr_repository.bot
  id = "vudrochka-bot"
}

import {
  to = aws_secretsmanager_secret.deploy
  id = "arn:aws:secretsmanager:eu-central-1:126568927381:secret:vudrochka-bot/deploy-9zmePe"
}

import {
  to = aws_lightsail_instance.bot
  id = "vudrochka-bot"
}
