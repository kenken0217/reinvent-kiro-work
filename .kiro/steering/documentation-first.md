---
inclusion: always
---

# Documentation-First Approach

This steering file encourages checking documentation before implementing solutions.

## Core Principle

**Always check official documentation and reliable sources before implementing or suggesting solutions.**

## When to Check Documentation

### AWS Services
- Before implementing AWS service integrations
- When encountering AWS-specific errors
- For CDK construct usage and best practices
- Use the AWS Knowledge MCP server: `mcp_aws_knowledge_mcp_server_aws___search_documentation`

### Python Libraries
- For Pydantic models and validation (check for v2 syntax changes)
- For FastAPI endpoints and features
- For boto3 DynamoDB operations
- Use Context7 MCP server for library documentation

### CDK and Infrastructure
- Before creating or modifying CDK stacks
- For Lambda function configurations
- For API Gateway setup
- Check AWS CDK documentation via MCP servers

## Available MCP Tools

You have access to the following MCP servers for documentation:

1. **AWS Knowledge Server** (`aws-kb-retrieval`):
   - Search AWS documentation
   - Get regional availability information
   - Read AWS documentation pages

2. **AWS CDK Server** (`aws-cdk`):
   - CDK best practices and guidance
   - CDK Nag rule explanations
   - GenAI CDK constructs

3. **Context7** (`context7`):
   - Library documentation (Pydantic, FastAPI, etc.)
   - Code examples and patterns
   - Up-to-date API references

4. **Brave Search** (`brave-search`):
   - Web search for general information
   - Finding recent updates and changes
   - Community solutions and discussions

5. **Fetch Server** (`fetch`):
   - Fetch and read web pages
   - Access online documentation

## Implementation Workflow

1. **Understand the requirement**
2. **Check documentation** using appropriate MCP tools
3. **Verify current best practices** (APIs change over time)
4. **Implement the solution** based on documentation
5. **Test and validate** the implementation

## Common Pitfalls to Avoid

- ❌ Using outdated syntax (e.g., Pydantic v1 `regex` instead of v2 `pattern`)
- ❌ Ignoring DynamoDB reserved keywords
- ❌ Not checking for recent API changes
- ❌ Assuming knowledge without verification

## Benefits

- ✅ Accurate implementations using current APIs
- ✅ Following official best practices
- ✅ Avoiding deprecated features
- ✅ Learning from official examples
- ✅ Staying updated with latest changes

## Example Usage

Before implementing a Pydantic model:
```
1. Search Context7 for "pydantic field validation"
2. Check for v2 syntax and changes
3. Implement using current best practices
```

Before using DynamoDB:
```
1. Search AWS docs for "DynamoDB reserved keywords"
2. Check boto3 documentation for proper syntax
3. Implement with ExpressionAttributeNames for reserved words
```

## Remember

**Documentation is your friend. Use it proactively, not reactively.**
