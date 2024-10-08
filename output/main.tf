provider "aws" {
  region = "ap-southeast-5"
}

resource "tls_private_key" "user_1" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "user_1" {
  key_name   = "User-1"
  public_key = tls_private_key.user_1.public_key_openssh
}

resource "aws_security_group" "server_1_sg" {
  name        = "Server-1-sg"
  description = "Security group for Server-1"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["182.35.46.18/32"]
  }

  ingress {
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = ["sg-0a9f8a8b8b8b8b8b"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "bucket_1" {
  bucket = "bucket-1"
}

resource "aws_iam_role" "ec2_role" {
  name = "ec2_s3_put_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "s3_put_policy" {
  name        = "s3_put_policy"
  description = "Policy to allow EC2 to put objects to Server-1-data bucket"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = "s3:PutObject",
        Effect   = "Allow",
        Resource = "arn:aws:s3:::Server-1-data/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.s3_put_policy.arn
}

resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "ec2_instance_profile"
  role = aws_iam_role.ec2_role.name
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_instance" "server_1" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.medium"
  key_name               = aws_key_pair.user_1.key_name
  security_groups        = [aws_security_group.server_1_sg.name]
  iam_instance_profile   = aws_iam_instance_profile.ec2_instance_profile.name

  tags = {
    Name  = "Server-1"
    Usage = "Lab"
  }

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update -y
              sudo apt-get upgrade -y
              sudo apt-get install -y nginx git
              git clone https://github.com/IBM-EPBL/ibm-cloud-pak-for-data.git /home/ec2-user/ibm-cloud-pak-for-data
              EOF
}
