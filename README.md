# AWS Cloud Infrastructure Automation with Terraform

## Project Overview

This project demonstrates the design, deployment, and management of a production-style AWS cloud infrastructure using **Terraform** and a Python-based API.

The infrastructure was deployed in AWS using a secure multi-tier architecture consisting of a public Application Load Balancer, private EC2 application servers, and a private PostgreSQL RDS database.

The project was built as a hands-on demonstration of:

* Infrastructure as Code (IaC)
* AWS networking
* Cloud security
* Infrastructure automation
* Load balancing
* Private application architecture
* Database connectivity
* Systems Manager access
* Terraform lifecycle management
* Cloud cost awareness

---

## Architecture

```text
                         Internet
                            |
                            v
                +-----------------------+
                |   Application Load    |
                |       Balancer        |
                |       Port 80         |
                +-----------+-----------+
                            |
                 +----------+----------+
                 |                     |
                 v                     v
        +----------------+    +----------------+
        |   EC2 Server   |    |   EC2 Server   |
        |    Private     |    |    Private     |
        |   Subnet #1    |    |   Subnet #2    |
        |   Port 8000    |    |   Port 8000    |
        +--------+-------+    +--------+-------+
                 |                     |
                 +----------+----------+
                            |
                            v
                 +----------------------+
                 |    RDS PostgreSQL    |
                 |       Private        |
                 |       Port 5432      |
                 +----------------------+
```

### Network Design

The VPC uses CIDR block:

```text
10.0.0.0/16
```

It contains:

* 2 public subnets
* 2 private subnets
* Public route table
* Private route table
* Internet Gateway
* VPC endpoints for AWS Systems Manager
* S3 Gateway VPC endpoint

The application servers and database are kept in private subnets.

---

## AWS Services Used

| Service                   | Purpose                          |
| ------------------------- | -------------------------------- |
| Amazon VPC                | Network isolation                |
| EC2                       | Application servers              |
| Application Load Balancer | Traffic distribution             |
| RDS PostgreSQL            | Relational database              |
| AWS Systems Manager       | Secure server access             |
| IAM                       | Access control                   |
| VPC Endpoints             | Private AWS service connectivity |
| S3                        | Gateway endpoint integration     |
| Terraform                 | Infrastructure as Code           |

---

## Application

The application is a lightweight Python HTTP API running on port `8000`.

### Endpoints

#### Health Check

```text
GET /health
```

Returns the health status of the application and the hostname of the EC2 instance handling the request.

Example:

```json
{
  "status": "healthy",
  "server": "ip-10-0-12-224.ec2.internal"
}
```

#### Cloud Costs

```text
GET /costs
```

Retrieves cloud cost records from the PostgreSQL database.

Example response:

```json
{
  "count": 3,
  "cloud_costs": [
    {
      "id": 1,
      "service_name": "EC2",
      "cost": 12.5,
      "usage_date": "2026-09-24"
    }
  ]
}
```

---

## Database

The project uses Amazon RDS PostgreSQL.

Database:

```text
cloudcost
```

The application stores cloud cost records in the `cloud_costs` table.

The database is **not publicly accessible**.

Database access is restricted using a security group that permits PostgreSQL traffic only from the application server security group.

---

## Security Design

Security was considered throughout the architecture.

### Private Application Servers

The EC2 instances do not have public IP addresses.

They are accessed using AWS Systems Manager rather than exposing SSH to the internet.

### Private Database

The RDS database is deployed privately and has:

```text
PubliclyAccessible = False
```

### Security Groups

Traffic is restricted between application layers.

```text
Internet
   |
   v
ALB :80
   |
   v
EC2 :8000
   |
   v
RDS :5432
```

The application security group accepts traffic on port `8000` only from the ALB security group.

The database security group accepts traffic on port `5432` only from the application security group.

### Credentials

Database credentials are supplied through Terraform variables rather than being hard-coded directly into the infrastructure configuration.

Sensitive Terraform variable files are excluded from Git using `.gitignore`.

AWS credentials are also kept outside the project repository.

---

## Infrastructure as Code

The entire AWS infrastructure is managed using Terraform.

This allows the infrastructure to be:

* Reproducible
* Version controlled
* Reviewed
* Modified consistently
* Destroyed when no longer required

Terraform was used to create and manage the networking, security groups, EC2 instances, load balancer, database, IAM resources, and VPC endpoints.

---

## Load Balancing

The Application Load Balancer distributes HTTP requests between two EC2 application servers.

Target health was verified through the AWS Load Balancer target group.

Both application servers successfully reached the:

```text
healthy
```

state.

The application was then tested through the public ALB endpoint.

This demonstrated the complete request path:

```text
Client
  ↓
Application Load Balancer
  ↓
Private EC2
  ↓
Private RDS PostgreSQL
```

---

## Testing

The deployed infrastructure was tested at multiple layers.

### Terraform

```bash
terraform validate
terraform plan
```

Terraform ultimately reported:

```text
No changes. Your infrastructure matches the configuration.
```

### EC2

Both application instances were verified as running.

### RDS

The database was verified as:

```text
available
```

and:

```text
PubliclyAccessible = False
```

### Load Balancer

The ALB was verified as:

```text
active
```

### Application

The API was tested through the ALB using:

```text
/health
```

and:

```text
/costs
```

The `/costs` endpoint successfully retrieved records from the PostgreSQL database.

---

## Cost Awareness

A major consideration during the project was avoiding unnecessary AWS costs.

The architecture intentionally avoided using a NAT Gateway because the private application servers did not require general outbound internet access.

Instead, AWS Systems Manager VPC endpoints and an S3 Gateway endpoint were used where appropriate.

The infrastructure can also be completely removed using:

```bash
terraform destroy
```

This prevents resources such as EC2, RDS, and the Application Load Balancer from continuing to run when the project is not being used.

---

## Project Structure

```text
aws-terraform-infrastructure/
│
├── main.tf
├── README.md
├── .gitignore
└── .terraform.lock.hcl
```

Sensitive and generated files such as:

```text
terraform.tfvars
terraform.tfstate
terraform.tfstate.backup
.terraform/
```

are excluded from version control.

---

## Skills Demonstrated

### AWS

* Amazon VPC
* Subnet design
* Route tables
* Security groups
* EC2
* RDS PostgreSQL
* Application Load Balancer
* IAM
* Systems Manager
* VPC endpoints

### Terraform

* Infrastructure as Code
* Resources
* Variables
* Security configuration
* Dependencies
* State management
* Terraform plan
* Terraform validation
* Terraform lifecycle configuration

### Python

* HTTP API development
* PostgreSQL connectivity
* JSON responses
* Error handling
* Environment variables
* Health checks

### Cloud Engineering

* Multi-tier architecture
* Private networking
* Least-privilege network access
* Load balancing
* Database isolation
* Infrastructure reproducibility
* Cost awareness

---

## What I Learned

This project provided hands-on experience designing and deploying a complete AWS environment rather than working with isolated AWS services.

Key lessons included:

1. Designing public and private network layers.
2. Restricting traffic using security groups.
3. Deploying application servers without public IP addresses.
4. Accessing private EC2 instances using Systems Manager.
5. Connecting applications securely to a private PostgreSQL database.
6. Using an Application Load Balancer to distribute traffic.
7. Managing AWS infrastructure using Terraform.
8. Separating sensitive configuration from source code.
9. Verifying infrastructure using AWS CLI and Terraform.
10. Considering AWS costs when designing cloud infrastructure.

---

## Future Improvements

Potential future improvements include:

* CI/CD using GitHub Actions
* Automated Terraform deployment
* HTTPS using AWS Certificate Manager
* Custom domain using Route 53
* CloudWatch monitoring and logging
* Auto Scaling Groups
* Terraform modules
* Secrets Manager integration
* Automated application deployment
* Cloud cost monitoring dashboard

---

## Cleanup

When the infrastructure is no longer required, it can be removed using:

```bash
terraform destroy
```

The Terraform source code remains available as the reproducible definition of the infrastructure.

---

## Author

Built as a hands-on AWS and Terraform cloud engineering portfolio project.
