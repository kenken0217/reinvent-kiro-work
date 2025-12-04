---
inclusion: manual
---

# AWS Credentials Management

This steering file helps maintain AWS credentials across terminal sessions.

## Important Guidelines

### When Running AWS CLI Commands

1. **Check for existing credentials first**:
   - Before running any AWS CLI command, check if credentials are already set
   - Use `aws sts get-caller-identity` to verify credentials

2. **Prompt for credentials when needed**:
   - If credentials are missing or expired, prompt the user to provide them
   - Ask the user to export the following environment variables:
     ```bash
     export AWS_DEFAULT_REGION="us-west-2"
     export AWS_ACCESS_KEY_ID="your-access-key"
     export AWS_SECRET_ACCESS_KEY="your-secret-key"
     export AWS_SESSION_TOKEN="your-session-token"
     ```

3. **Avoid creating new terminals unnecessarily**:
   - Reuse existing terminal sessions when possible
   - New terminals lose environment variables including AWS credentials
   - If a new terminal is required, remind the user to re-export credentials

4. **Use the same terminal for related commands**:
   - When running multiple AWS commands, use the same terminal session
   - This preserves environment variables across commands

## CDK Deployment Guidelines

When deploying with CDK:

1. Always run CDK commands in the `infrastructure` directory
2. Ensure AWS credentials are set before running `cdk deploy`
3. If deployment fails due to credentials, prompt user to re-export them
4. Use `--require-approval never` flag to avoid interactive prompts

## Error Handling

If you encounter AWS credential errors:
- `InvalidAccessKeyId`: Credentials are incorrect or not set
- `ExpiredToken`: Session token has expired
- `AccessDenied`: Credentials lack necessary permissions

When these occur, inform the user and ask them to provide fresh credentials.

## Best Practices

- Never hardcode AWS credentials in code
- Always use environment variables or AWS credential files
- Remind users that temporary credentials expire
- Suggest using AWS SSO or IAM roles for long-term access
