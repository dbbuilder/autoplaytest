# VPC for Lambda functions (required for Playwright)
resource "aws_vpc" "main" {
  count = var.enable_vpc ? 1 : 0
  
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "${local.prefix}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  count = var.enable_vpc ? 1 : 0
  
  vpc_id = aws_vpc.main[0].id
  
  tags = {
    Name = "${local.prefix}-igw"
  }
}

# Elastic IP for NAT Gateway
resource "aws_eip" "nat" {
  count = var.enable_vpc ? length(data.aws_availability_zones.available.names) : 0
  
  domain = "vpc"
  
  tags = {
    Name = "${local.prefix}-nat-eip-${count.index + 1}"
  }
}

# NAT Gateway (one per AZ for high availability)
resource "aws_nat_gateway" "main" {
  count = var.enable_vpc ? length(data.aws_availability_zones.available.names) : 0
  
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  tags = {
    Name = "${local.prefix}-nat-gateway-${count.index + 1}"
  }
  
  depends_on = [aws_internet_gateway.main]
}

# Public Subnets (for NAT Gateways)
resource "aws_subnet" "public" {
  count = var.enable_vpc ? length(data.aws_availability_zones.available.names) : 0
  
  vpc_id                  = aws_vpc.main[0].id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = {
    Name = "${local.prefix}-public-subnet-${count.index + 1}"
    Type = "Public"
  }
}

# Private Subnets (for Lambda functions)
resource "aws_subnet" "private" {
  count = var.enable_vpc ? length(data.aws_availability_zones.available.names) : 0
  
  vpc_id            = aws_vpc.main[0].id
  cidr_block        = "10.0.${count.index + 100}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "${local.prefix}-private-subnet-${count.index + 1}"
    Type = "Private"
  }
}

# Route table for public subnets
resource "aws_route_table" "public" {
  count = var.enable_vpc ? 1 : 0
  
  vpc_id = aws_vpc.main[0].id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main[0].id
  }
  
  tags = {
    Name = "${local.prefix}-public-rt"
  }
}

# Route tables for private subnets (one per AZ)
resource "aws_route_table" "private" {
  count = var.enable_vpc ? length(data.aws_availability_zones.available.names) : 0
  
  vpc_id = aws_vpc.main[0].id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }
  
  tags = {
    Name = "${local.prefix}-private-rt-${count.index + 1}"
  }
}

# Route table associations
resource "aws_route_table_association" "public" {
  count = var.enable_vpc ? length(aws_subnet.public) : 0
  
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public[0].id
}

resource "aws_route_table_association" "private" {
  count = var.enable_vpc ? length(aws_subnet.private) : 0
  
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# Security Group for Lambda functions
resource "aws_security_group" "lambda" {
  count = var.enable_vpc ? 1 : 0
  
  name        = "${local.prefix}-lambda-sg"
  description = "Security group for Lambda functions"
  vpc_id      = aws_vpc.main[0].id
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = {
    Name = "${local.prefix}-lambda-sg"
  }
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}