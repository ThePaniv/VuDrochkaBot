# Deploy target for the CD workflow (Lightsail host + ubuntu user + private key).
#
# Only the secret CONTAINER is managed here. The VALUE is deliberately NOT in
# Terraform — secret material must not live in state or the repo. Set/rotate it
# out-of-band, e.g.:
#   aws secretsmanager put-secret-value --secret-id vudrochka-bot/deploy \
#     --secret-string '{"host":"...","user":"ubuntu","ssh_key":"-----BEGIN..."}'
resource "aws_secretsmanager_secret" "deploy" {
  name        = "vudrochka-bot/deploy"
  description = "Lightsail deploy target: host, ubuntu, default-keypair private key"
}
