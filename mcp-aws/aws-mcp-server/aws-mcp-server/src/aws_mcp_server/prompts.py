"""AWS CLI prompt definitions for the AWS MCP Server.

This module provides a collection of useful prompt templates for common AWS use cases.
These prompts help ensure consistent best practices and efficient AWS resource management.
"""

import logging

logger = logging.getLogger(__name__)


def register_prompts(mcp):
    """Register all prompts with the MCP server instance.

    Args:
        mcp: The FastMCP server instance
    """
    logger.info("Registering AWS prompt templates")

    @mcp.prompt(name="create_resource", description="Generate AWS CLI commands to create common AWS resources with best practices")
    def create_resource(resource_type: str, resource_name: str) -> str:
        """Generate AWS CLI commands to create common AWS resources with best practices.

        Args:
            resource_type: Type of AWS resource to create (e.g., s3-bucket, ec2-instance, lambda)
            resource_name: Name for the new resource

        Returns:
            Formatted prompt string for resource creation
        """
        return f"""Generate the AWS CLI commands to create a new {resource_type} named {resource_name} 
following AWS Well-Architected Framework best practices.

Please include:
1. The primary creation command with appropriate security settings
2. Any supporting resources needed (roles, policies, etc.)
3. Required tagging commands (Name, Environment, Purpose, Owner, Cost-Center)
4. Security hardening commands to enforce principle of least privilege
5. Encryption and data protection configuration
6. Verification commands to confirm successful creation

Ensure the solution includes:
- Proper encryption at rest and in transit
- Secure access control mechanisms
- Resource policies with appropriate permissions
- Monitoring and logging setup with CloudWatch
- Cost optimization considerations

For IAM roles and policies, follow the principle of least privilege and explain any important 
security considerations specific to this resource type."""

    @mcp.prompt(name="security_audit", description="Generate AWS CLI commands for performing a security audit on a service")
    def security_audit(service: str) -> str:
        """Generate AWS CLI commands for performing a security audit on a service.

        Args:
            service: AWS service to audit (e.g., s3, ec2, iam, rds)

        Returns:
            Formatted prompt string for security auditing
        """
        return f"""Generate AWS CLI commands to perform a comprehensive security audit
of {service} resources in my AWS account according to AWS Security Hub and Well-Architected Framework.

Include commands to:
1. Identify resources with public access, excessive permissions, or security group vulnerabilities
2. Detect weak or unused security configurations and access controls
3. Check for unencrypted data (both at rest and in transit)
4. Verify enabled logging and monitoring capabilities 
5. Assess IAM roles and policies attached to resources for overly permissive settings
6. Check for resource compliance with CIS AWS Foundations Benchmark
7. Identify potential security misconfigurations based on AWS security best practices
8. Detect unused credentials, access keys, and permissions

Also provide:
- Security findings categorized by severity (High, Medium, Low)
- A prioritized list of remediation steps with corresponding CLI commands
- Recommendations to implement automated security checks using AWS Config Rules"""

    @mcp.prompt(name="cost_optimization", description="Generate AWS CLI commands for cost optimization recommendations")
    def cost_optimization(service: str) -> str:
        """Generate AWS CLI commands for cost optimization recommendations.

        Args:
            service: AWS service to optimize costs for

        Returns:
            Formatted prompt string for cost optimization
        """
        return f"""Generate AWS CLI commands to identify cost optimization opportunities 
for {service} in my AWS account using AWS Cost Explorer and other cost management tools.

Include commands to:
1. Find unused, idle, or underutilized resources with detailed utilization metrics
2. Identify resources that could be rightsized, downsized, or use a different pricing model
3. Detect patterns of usage that could benefit from Reserved Instances, Savings Plans, or Spot instances
4. Analyze resources without proper cost allocation tags and suggest tagging strategies
5. Generate a detailed cost breakdown by resource for the past 30 days
6. Identify optimal instance families based on workload patterns
7. Find opportunities to utilize AWS Graviton processors for better price-performance ratio
8. Check for resources that can leverage multi-region strategies for cost efficiency

Also provide:
- Cost-saving estimates for each recommendation
- Commands to implement automated cost management using AWS Budgets
- Scripts to schedule automated start/stop for dev/test environments
- Best practices for implementing FinOps for {service}"""

    @mcp.prompt(name="resource_inventory", description="Generate AWS CLI commands to inventory resources for a service")
    def resource_inventory(service: str, region: str = "all") -> str:
        """Generate AWS CLI commands to inventory resources for a service.

        Args:
            service: AWS service to inventory (e.g., s3, ec2, rds)
            region: AWS region or "all" for multi-region inventory

        Returns:
            Formatted prompt string for resource inventory
        """
        region_text = f"in the {region} region" if region != "all" else "across all regions"

        return f"""Generate AWS CLI commands to create a comprehensive inventory 
of all {service} resources {region_text}.

Include commands to:
1. List all resources with their key properties, metadata, and creation dates
2. Show resource relationships, dependencies, and associated infrastructure
3. Display resource tags, ownership information, and cost allocation
4. Identify untagged, potentially abandoned, or non-compliant resources
5. Export the inventory in structured formats (JSON, CSV) for further analysis
6. Group resources by type, status, size, and configuration
7. Include usage metrics and performance data where applicable
8. List attached IAM roles, policies, and security configurations

Structure the commands to output to easily parsable formats that can be programmatically processed.
Include jq filters to transform complex JSON output into useful summaries."""

    @mcp.prompt(name="troubleshoot_service", description="Generate AWS CLI commands for troubleshooting service issues")
    def troubleshoot_service(service: str, resource_id: str) -> str:
        """Generate AWS CLI commands for troubleshooting service issues.

        Args:
            service: AWS service to troubleshoot (e.g., ec2, rds, lambda)
            resource_id: ID of the specific resource having issues

        Returns:
            Formatted prompt string for troubleshooting
        """
        return f"""Generate AWS CLI commands to troubleshoot issues with {service} 
resource {resource_id} using a systematic diagnostic approach.

Include commands to:
1. Check resource status, health, configuration, and performance metrics
2. Review recent changes, modifications, deployments, or infrastructure updates
3. Examine detailed logs, metrics, alarm history, and error patterns from CloudWatch
4. Verify network connectivity, security groups, NACLs, and routing settings
5. Diagnose potential service limits, throttling, or quota issues
6. Check for dependent services and connectivity between resources
7. Analyze IAM permissions and resource policies that might affect access
8. Validate configuration against AWS best practices and common failure patterns

Structure the troubleshooting as a systematic process from:
- Basic health and status verification
- Configuration and recent changes analysis
- Performance and resource utilization assessment
- Network and connectivity validation
- IAM and security verification
- Dependent services analysis
- Logging and monitoring data collection

Include commands to collect all relevant diagnostic information into a single report that can be shared with AWS Support if needed."""

    @mcp.prompt(name="iam_policy_generator", description="Generate least-privilege IAM policies for specific services and actions")
    def iam_policy_generator(service: str, actions: str, resource_pattern: str = "*") -> str:
        """Generate least-privilege IAM policies for specific services and actions.

        Args:
            service: AWS service for the policy (e.g., s3, dynamodb)
            actions: Comma-separated list of actions (e.g., "GetObject,PutObject")
            resource_pattern: Resource ARN pattern (e.g., "arn:aws:s3:::my-bucket/*")

        Returns:
            Formatted prompt string for IAM policy generation
        """
        return f"""Generate a least-privilege IAM policy that allows only the required permissions
for {service} with these specific actions: {actions}.

Resource pattern: {resource_pattern}

The policy should:
1. Follow AWS IAM security best practices and use the latest policy structure
2. Include only the minimum permissions needed for the stated actions
3. Use proper condition keys to restrict access by source IP, VPC, time, MFA, etc.
4. Implement appropriate resource-level permissions where supported
5. Include explanatory comments for each permission block
6. Use AWS managed policies where appropriate to reduce maintenance overhead
7. Be ready to use with the AWS CLI for policy creation

Also provide:
- The AWS CLI command to apply this policy to a role or user
- Best practice recommendations for using policy boundaries
- Explanation of potential security impact if permissions are too broad
- Alternative permissions strategies if applicable (e.g., attribute-based access control)"""

    @mcp.prompt(name="service_monitoring", description="Generate AWS CLI commands to set up monitoring for a service")
    def service_monitoring(service: str, metric_type: str = "performance") -> str:
        """Generate AWS CLI commands to set up monitoring for a service.

        Args:
            service: AWS service to monitor (e.g., ec2, rds, lambda)
            metric_type: Type of metrics to monitor (e.g., performance, cost, security)

        Returns:
            Formatted prompt string for monitoring setup
        """
        return f"""Generate AWS CLI commands to set up comprehensive {metric_type} monitoring 
for {service} resources using CloudWatch, X-Ray, and other observability tools.

Include commands to:
1. Create CloudWatch dashboards with relevant metrics and service-specific KPIs
2. Set up appropriate CloudWatch alarms with actionable thresholds and anomaly detection
3. Configure detailed logging with Log Insights queries for common analysis patterns
4. Enable AWS X-Ray tracing for distributed systems analysis where applicable
5. Create SNS topics and subscription for multi-channel notifications (email, Slack, PagerDuty)
6. Set up metric filters to extract critical information from log patterns
7. Configure composite alarms for complex monitoring scenarios
8. Enable AWS Service Health Dashboard notifications for service issues

The monitoring solution should include:
- Resource-specific metrics that indicate health and performance
- Operational thresholds based on industry best practices
- Multi-tier alerting with different severity levels
- Automated remediation actions where appropriate
- Integration with incident management workflows

Ensure the commands follow operational excellence best practices from the Well-Architected Framework."""

    @mcp.prompt(name="disaster_recovery", description="Generate AWS CLI commands to implement disaster recovery for a service")
    def disaster_recovery(service: str, recovery_point_objective: str = "1 hour") -> str:
        """Generate AWS CLI commands to implement disaster recovery for a service.

        Args:
            service: AWS service to protect (e.g., ec2, rds, dynamodb)
            recovery_point_objective: Target RPO (e.g., "1 hour", "15 minutes")

        Returns:
            Formatted prompt string for DR setup
        """
        return f"""Generate AWS CLI commands to implement a disaster recovery solution
for {service} with a Recovery Point Objective (RPO) of {recovery_point_objective} and minimal Recovery Time Objective (RTO).

Include commands to:
1. Configure appropriate backup mechanisms (snapshots, replication, AWS Backup)
2. Set up cross-region or cross-account redundancy with proper data synchronization
3. Create automation for recovery processes using AWS Systems Manager documents
4. Implement comprehensive monitoring and alerting for backup failures
5. Define validation procedures to verify recovery readiness and integrity
6. Setup regular DR testing through automation
7. Configure failover mechanisms and DNS routing strategies using Route 53
8. Implement data integrity checks for backups and replicas

The solution should:
- Balance cost effectiveness with meeting the specified RPO
- Follow AWS Well-Architected Framework best practices for reliability
- Include automated recovery procedures that minimize manual intervention
- Provide appropriate IAM roles and permissions for DR operations
- Consider regional service availability differences
- Include both data and configuration recovery"""

    @mcp.prompt(name="compliance_check", description="Generate AWS CLI commands to check compliance with standards")
    def compliance_check(compliance_standard: str, service: str = "all") -> str:
        """Generate AWS CLI commands to check compliance with standards.

        Args:
            compliance_standard: Compliance standard to check (e.g., "HIPAA", "PCI", "GDPR")
            service: Specific AWS service or "all" for account-wide checks

        Returns:
            Formatted prompt string for compliance checking
        """
        service_scope = f"for {service}" if service != "all" else "across all relevant services"

        return f"""Generate AWS CLI commands to assess {compliance_standard} compliance {service_scope}
using AWS Config, AWS Security Hub, and AWS Audit Manager.

Include commands to:
1. Identify resources that may not meet {compliance_standard} compliance requirements
2. Check encryption settings, key management, and data protection measures
3. Audit access controls, authentication mechanisms, and privilege management
4. Verify logging, monitoring configurations, and audit trail completeness
5. Assess network security, isolation, and boundary protection
6. Evaluate resource configurations against specific {compliance_standard} controls
7. Check for compliant tagging and resource documentation
8. Analyze retention policies for backups, logs, and archived data

Also provide:
- Remediation commands for common compliance gaps with {compliance_standard}
- Explanation of specific {compliance_standard} requirements being checked
- Commands to generate compliance reports using AWS Audit Manager
- Instructions to set up continuous compliance monitoring
- Best practices for maintaining ongoing compliance"""

    @mcp.prompt(name="resource_cleanup", description="Generate AWS CLI commands to identify and cleanup unused resources")
    def resource_cleanup(service: str, criteria: str = "unused") -> str:
        """Generate AWS CLI commands to identify and cleanup unused resources.

        Args:
            service: AWS service to cleanup (e.g., ec2, ebs, rds)
            criteria: Criteria for cleanup (e.g., "unused", "old", "untagged")

        Returns:
            Formatted prompt string for resource cleanup
        """
        return f"""Generate AWS CLI commands to identify and safely clean up {criteria} {service} resources
to reduce costs and improve account hygiene.

Include commands to:
1. Identify resources matching the {criteria} criteria with appropriate filters and metrics
2. Generate a detailed report of resources before deletion for review and approval
3. Create backups, snapshots, or exports where appropriate before removal
4. Safely delete or terminate the identified resources with proper validation
5. Verify successful cleanup and calculate actual cost savings
6. Check for orphaned dependent resources (volumes, snapshots, ENIs)
7. Identify resources that could be scheduled for regular cleanup
8. Capture resource metadata before deletion for audit purposes

The commands should include:
- Appropriate safeguards to prevent accidental deletion of critical resources
- Dry-run options to preview changes before execution
- Validation checks to ensure resources are truly unused
- Tag-based identification of approved resources to preserve
- Staged approach that isolates resources before deletion
- Estimate of cost savings from cleanup activities

Follow AWS operational best practices and include error handling."""

    @mcp.prompt(name="serverless_deployment", description="Generate AWS CLI commands to deploy a serverless application")
    def serverless_deployment(application_name: str, runtime: str = "python3.13") -> str:
        """Generate AWS CLI commands to deploy a serverless application.

        Args:
            application_name: Name for the serverless application
            runtime: Runtime environment (e.g., "python3.13", "nodejs20.x", "java17")

        Returns:
            Formatted prompt string for serverless deployment
        """
        return f"""Generate AWS CLI commands to deploy a serverless application named {application_name} 
using AWS SAM, Lambda, API Gateway, and DynamoDB with {runtime} runtime.

Include commands to:
1. Initialize a new SAM application with best practices structure
2. Create necessary Lambda functions with appropriate IAM roles
3. Set up API Gateway endpoints with proper authorization
4. Deploy DynamoDB tables with optimal capacity and indexing
5. Configure CloudWatch Logs and X-Ray tracing
6. Set up CI/CD pipeline using AWS CodePipeline
7. Implement proper versioning and deployment strategies (canary, linear)
8. Create CloudFormation custom resources if needed

The deployment should follow serverless best practices:
- Appropriate function timeouts and memory allocation
- Least privilege IAM permissions for each component
- Parameter Store or Secrets Manager for configuration
- Proper error handling and dead-letter queues
- Efficient cold start optimization
- Secure API authorization (JWT, IAM, Cognito)
- Cost-effective resource utilization

Include commands to verify the deployment and test the application endpoints."""

    @mcp.prompt(name="container_orchestration", description="Generate AWS CLI commands to set up container orchestration")
    def container_orchestration(cluster_name: str, service_type: str = "fargate") -> str:
        """Generate AWS CLI commands to set up container orchestration.

        Args:
            cluster_name: Name for the ECS/EKS cluster
            service_type: Type of service (e.g., "fargate", "ec2", "eks")

        Returns:
            Formatted prompt string for container deployment
        """
        return f"""Generate AWS CLI commands to set up a container orchestration environment 
with a {service_type} cluster named {cluster_name} following AWS best practices.

Include commands to:
1. Create the {service_type} cluster with appropriate networking and security settings
2. Set up necessary IAM roles, task execution roles, and service roles
3. Configure task definitions with optimal resource allocation
4. Deploy services with appropriate scaling policies and load balancing
5. Implement service discovery and container insights monitoring
6. Set up logging and metric collection for containers
7. Configure secrets management for sensitive configuration
8. Implement proper security controls (ECR scanning, networking)

The commands should address:
- Proper networking design with security groups and VPC settings
- Auto-scaling based on CPU, memory, and custom metrics
- CI/CD pipeline integration for container deployment
- Health checks and graceful deployment strategies
- Container image security scanning and validation
- Efficient resource utilization and cost management
- High availability across multiple availability zones
- Secrets and environment variable management

Include validation commands to verify successful deployment and access."""

    @mcp.prompt(name="vpc_network_design", description="Generate AWS CLI commands to design and deploy a secure VPC")
    def vpc_network_design(vpc_name: str, cidr_block: str = "10.0.0.0/16") -> str:
        """Generate AWS CLI commands to design and deploy a secure VPC.

        Args:
            vpc_name: Name for the VPC
            cidr_block: CIDR block for the VPC (e.g., "10.0.0.0/16")

        Returns:
            Formatted prompt string for VPC design
        """
        return f"""Generate AWS CLI commands to design and deploy a secure, well-architected VPC
named {vpc_name} with CIDR block {cidr_block} following AWS networking best practices.

Include commands to:
1. Create the VPC with appropriate DNS and tenancy settings
2. Set up public and private subnets across multiple availability zones
3. Configure Internet Gateway, NAT Gateways, and route tables
4. Implement Network ACLs and security groups with least-privilege rules
5. Set up VPC endpoints for AWS services to improve security
6. Configure VPC Flow Logs for network traffic monitoring
7. Implement Transit Gateway or VPC Peering if needed
8. Set up DNS management with Route 53

The VPC design should include:
- High availability across at least 3 availability zones
- Secure subnet segmentation (public, private, data)
- Proper CIDR block allocation for future expansion
- Security controls at multiple layers (NACLs, security groups)
- Efficient routing and traffic flow optimization
- Private connectivity to AWS services using endpoints
- Network traffic monitoring and logging
- Disaster recovery considerations

Include validation commands to verify the network connectivity and security."""

    @mcp.prompt(name="infrastructure_automation", description="Generate AWS CLI commands for infrastructure automation")
    def infrastructure_automation(resource_type: str, automation_scope: str = "deployment") -> str:
        """Generate AWS CLI commands for infrastructure automation.

        Args:
            resource_type: Type of AWS resource to automate (e.g., ec2, rds, lambda)
            automation_scope: Type of automation (e.g., "deployment", "scaling", "patching")

        Returns:
            Formatted prompt string for infrastructure automation
        """
        return f"""Generate AWS CLI commands to implement {automation_scope} automation 
for {resource_type} resources using AWS Systems Manager, CloudFormation, and EventBridge.

Include commands to:
1. Create automation documents or CloudFormation templates for consistent {automation_scope}
2. Set up EventBridge rules to trigger automation on schedule or event patterns
3. Configure necessary IAM roles and permissions with least privilege
4. Implement parameter validation and error handling in automation scripts
5. Set up notification and reporting for automation results
6. Create maintenance windows and safe deployment practices
7. Implement automated rollback mechanisms for failures
8. Configure cross-account or cross-region automation if needed

The automation solution should:
- Minimize manual intervention while maintaining appropriate approvals
- Include proper logging and audit trails for all activities
- Handle edge cases and failure scenarios gracefully
- Scale to manage multiple resources efficiently
- Follow infrastructure as code best practices
- Include proper testing and validation steps
- Respect maintenance windows and business hours
- Provide detailed reporting and status tracking

Include commands to validate the automation and test it in a controlled environment."""

    @mcp.prompt(name="security_posture_assessment", description="Generate AWS CLI commands for comprehensive security posture assessment")
    def security_posture_assessment() -> str:
        """Generate AWS CLI commands for comprehensive security posture assessment.

        Returns:
            Formatted prompt string for security assessment
        """
        return """Generate AWS CLI commands to perform a comprehensive security posture assessment
across your AWS environment using Security Hub, IAM Access Analyzer, and GuardDuty.

Include commands to:
1. Enable and configure AWS Security Hub with appropriate standards
2. Setup AWS Config for resource configuration monitoring
3. Enable GuardDuty for threat detection across all regions
4. Configure IAM Access Analyzer to identify external access
5. Review CloudTrail for complete activity logging coverage
6. Assess S3 bucket policies and access controls
7. Analyze password policies and MFA implementation
8. Evaluate network security groups and NACLs

The assessment should check for:
- Identity and access management best practices
- Data protection mechanisms and encryption
- Infrastructure security configurations
- Detective controls and logging completeness
- Compliance with industry standards (CIS, NIST, PCI)
- Privileged access management
- Potential lateral movement paths
- Security monitoring and incident response readiness

Include commands to generate comprehensive reports of findings organized by severity,
and provide remediation steps for common security issues."""

    @mcp.prompt(name="performance_tuning", description="Generate AWS CLI commands for performance tuning of AWS resources")
    def performance_tuning(service: str, resource_id: str) -> str:
        """Generate AWS CLI commands for performance tuning of AWS resources.

        Args:
            service: AWS service to optimize (e.g., rds, ec2, lambda)
            resource_id: ID of the specific resource to tune

        Returns:
            Formatted prompt string for performance tuning
        """
        return f"""Generate AWS CLI commands to analyze and tune the performance of {service} 
resource {resource_id} based on metrics, benchmarks, and AWS best practices.

Include commands to:
1. Gather detailed performance metrics using CloudWatch over various time periods
2. Analyze resource configuration and compare to recommended settings
3. Identify performance bottlenecks and resource constraints
4. Modify configuration parameters for optimal performance
5. Implement caching strategies if applicable
6. Adjust scaling policies and resource allocation
7. Configure enhanced monitoring for detailed insights
8. Benchmark performance before and after changes

The performance tuning approach should:
- Establish baseline performance metrics before changes
- Target specific performance issues with measured approaches
- Consider workload patterns and usage characteristics
- Balance performance improvements with cost implications
- Implement changes in staged approach with validation
- Document performance gains and configuration changes
- Address both immediate bottlenecks and long-term scaling

Include commands to verify performance improvements and monitor for regressions."""

    @mcp.prompt(name="multi_account_governance", description="Generate AWS CLI commands to implement multi-account governance")
    def multi_account_governance(account_type: str = "organization") -> str:
        """Generate AWS CLI commands to implement multi-account governance.

        Args:
            account_type: Type of account structure (e.g., "organization", "control tower")

        Returns:
            Formatted prompt string for multi-account governance
        """
        return f"""Generate AWS CLI commands to implement robust multi-account governance
using AWS Organizations, Control Tower, and {account_type} best practices.

Include commands to:
1. Set up organizational units (OUs) with logical account grouping
2. Implement service control policies (SCPs) for security guardrails
3. Configure centralized logging with CloudTrail and CloudWatch Logs
4. Set up cross-account IAM roles with least privilege
5. Implement tag policies and resource tagging strategies
6. Configure AWS Config for multi-account compliance monitoring
7. Set up centralized security monitoring with Security Hub
8. Implement account baselining and standardization

The governance framework should address:
- Preventative guardrails using SCPs and permission boundaries
- Detective controls with centralized logging and monitoring
- Cost management and billing consolidation
- Standardized network architecture across accounts
- Identity federation and cross-account access
- Centralized audit and compliance reporting
- Automated account provisioning and baseline configuration
- Resource sharing and cross-account service usage

Include guidance on implementing a secure landing zone and account structure."""

    logger.info("Successfully registered all AWS prompt templates")
