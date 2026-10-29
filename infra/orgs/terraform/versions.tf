# B6-3. Static Terraform track for the Organizations guard rails.
# Not applied. No real account. `terraform validate` does not call AWS when the provider
# skips credentials and account lookup. The CDK module remains the policy source;
# `npm run export:policies` writes evidence/orgs/policies/*.json, which this module reads.

terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.70.0, < 6.0.0"
    }
  }
}

provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_requesting_account_id = true
  skip_metadata_api_check     = true
  skip_region_validation      = true
}
