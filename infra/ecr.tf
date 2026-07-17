# Container registry the deploy workflow pushes to and the Lightsail box pulls from.
resource "aws_ecr_repository" "bot" {
  name                 = "vudrochka-bot"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  # Deleting the repo would drop every image the bot runs from.
  lifecycle {
    prevent_destroy = true
  }
}
