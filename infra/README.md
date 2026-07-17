# infra/ — Terraform for VuDrochkaBot's AWS resources

Infrastructure-as-code for everything the bot's deploy pipeline depends on, in
account `126568927381` / `eu-central-1`.

## What's managed here

| Resource | Terraform address | Notes |
|---|---|---|
| GitHub OIDC provider | `aws_iam_openid_connect_provider.github` | lets Actions assume roles without keys |
| Deploy role | `aws_iam_role.deploy` | `github-actions-vudrochka-deploy`, trust scoped to this repo's `deploy`/`develop` |
| Role policies | `aws_iam_role_policy.ecr_push`, `.secrets_read` | ECR push + read the deploy secret |
| ECR repo | `aws_ecr_repository.bot` | `vudrochka-bot` (`prevent_destroy`) |
| Deploy secret | `aws_secretsmanager_secret.deploy` | container only — **value is not in Terraform** |
| Lightsail instance | `aws_lightsail_instance.bot` | the box (`prevent_destroy`) |

**Not managed here:** the deploy secret's *value* (host + SSH key — secret material,
set out-of-band), the box's `~/vudrochka/.env` (`BOT_TOKEN`), and the legacy
ECS/Fargate resources (being decommissioned).

## Prerequisites

- Terraform ≥ 1.6.
- AWS CLI profile `claude` (or override: `-var aws_profile=<name>`).

## Usage

```bash
cd infra
terraform init
terraform plan     # should show no changes — this repo mirrors live infra
terraform apply    # only when you intend to change infra
```

## State

State is **local** (`terraform.tfstate`) and git-ignored because it can contain
sensitive values. If you work from more than one machine or want durability,
switch to an S3 backend in `versions.tf` and `terraform init -migrate-state`.

## How this was created

The resources were first created imperatively (AWS CLI) to unblock the deploy,
then imported into Terraform so the code matches reality without recreating
anything. The `import` blocks used are kept in `imports.tf` for reference; they
are idempotent and can stay.
