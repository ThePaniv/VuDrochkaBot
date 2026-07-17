# The box the bot runs on. Its disk holds ~/vudrochka/.env (BOT_TOKEN), the
# swapfile, and Docker state — recreating it would wipe all of that, so it is
# guarded with prevent_destroy.
resource "aws_lightsail_instance" "bot" {
  name              = "vudrochka-bot"
  availability_zone = "eu-central-1a"
  blueprint_id      = "ubuntu_24_04"
  bundle_id         = "nano_3_0" # $5/mo, 512MB, IPv4 (not the ipv6-only bundle)
  key_pair_name     = "LightsailDefaultKeyPair"

  lifecycle {
    prevent_destroy = true
    # user_data only runs at first boot; the box has since been configured by
    # hand, so don't let a config value here trigger a replace.
    ignore_changes = [user_data]
  }
}
