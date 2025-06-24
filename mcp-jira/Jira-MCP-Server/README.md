# Jira MCP Server

[![smithery badge](https://smithery.ai/badge/@George5562/Jira-MCP-Server)](https://smithery.ai/server/@George5562/Jira-MCP-Server)
[![MCP](https://badge.mcpx.dev/default)](https://modelcontextprotocol.io)
[![Claude](https://img.shields.io/badge/Claude-AI-D79943)](https://claude.ai)
[![Cursor](https://img.shields.io/badge/Cursor-Editor-009EFF)](https://cursor.sh)

Speak to Jira in natural language to get information on and modify your project. Use it with Claude Desktop in combination with a custom README that you will create with project information, so that you can delegate PM tasks, (e.g. given yoou have a list of my team and their specialities, assign any new issue to the most relevant person).

Built using the [Model Context Protocol](https://github.com/modelcontextprotocol).

<a href="https://glama.ai/mcp/servers/lblw6pvk7i">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/lblw6pvk7i/badge" alt="Jira Server MCP server" />
</a>

The server enables:

- Project creation and configuration
- Issue and subtask management
- Issue linking and dependencies
- Automated issue workflows

## Configuration

Required environment variables:

- `JIRA_HOST`: Your Jira instance hostname
- `JIRA_EMAIL`: Your Jira account email
- `JIRA_API_TOKEN`: API token from https://id.atlassian.com/manage-profile/security/api-tokens

## Available Tools

### 1. User Management

```typescript
// Get user's account ID by email
{
  email: "user@example.com";
}
```

### 2. Issue Type Management

```typescript
// List all available issue types
// Returns: id, name, description, subtask status
// No parameters required
```

### 3. Issue Link Types

```typescript
// List all available issue link types
// Returns: id, name, inward/outward descriptions
// No parameters required
```

### 4. Issue Management

#### Retrieving Issues

```typescript
// Get all issues in a project
{
  projectKey: "PROJECT"
}

// Get issues with JQL filtering
{
  projectKey: "PROJECT",
  jql: "status = 'In Progress' AND assignee = currentUser()"
}

// Get issues assigned to user
{
  projectKey: "PROJECT",
  jql: "assignee = 'user@example.com' ORDER BY created DESC"
}
```

#### Creating Issues

```typescript
// Create a standard issue
{
  projectKey: "PROJECT",
  summary: "Issue title",
  issueType: "Task",  // or "Story", "Bug", etc.
  description: "Detailed description",
  assignee: "accountId",  // from get_user tool
  labels: ["frontend", "urgent"],
  components: ["ui", "api"],
  priority: "High"
}

// Create a subtask
{
  parent: "PROJECT-123",
  projectKey: "PROJECT",
  summary: "Subtask title",
  issueType: "Subtask",
  description: "Subtask details",
  assignee: "accountId"
}
```

#### Updating Issues

```typescript
// Update issue fields
{
  issueKey: "PROJECT-123",
  summary: "Updated title",
  description: "New description",
  assignee: "accountId",
  status: "In Progress",
  priority: "High"
}
```

#### Issue Dependencies

```typescript
// Create issue link
{
  linkType: "Blocks",  // from list_link_types
  inwardIssueKey: "PROJECT-124",  // blocked issue
  outwardIssueKey: "PROJECT-123"  // blocking issue
}
```

#### Deleting Issues

```typescript
// Delete single issue
{
  issueKey: "PROJECT-123"
}

// Delete issue with subtasks
{
  issueKey: "PROJECT-123",
  deleteSubtasks: true
}

// Delete multiple issues
{
  issueKeys: ["PROJECT-123", "PROJECT-124"]
}
```

## Field Formatting

### Description Field

The description field supports markdown-style formatting:

- Use blank lines between paragraphs
- Use "- " for bullet points
- Use "1. " for numbered lists
- Use headers ending with ":" (followed by blank line)

Example:

```
Task Overview:

This task involves implementing new features:
- Feature A implementation
- Feature B testing

Steps:
1. Design component
2. Implement logic
3. Add tests

Acceptance Criteria:
- All tests passing
- Documentation updated
```

## Error Handling

The server provides detailed error messages for:

- Invalid issue keys
- Missing required fields
- Permission issues
- API rate limits

## Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/George5562/Jira-MCP-Server.git
   cd Jira-MCP-Server
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Configure environment variables:
   Create a `.env` file in the root directory:

   ```bash
   JIRA_HOST=your-instance.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-api-token
   ```

4. Build the project:

   ```bash
   npm run build
   ```

5. Start the server:
   ```bash
   npm start
   ```

## Configuring Claude Desktop

To use this MCP server with Claude Desktop:

1. Locate your Claude Desktop configuration file:

   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add the Jira MCP server to your configuration:

   ```json
   {
     "mcpServers": {
       "jira-server": {
         "name": "jira-server",
         "command": "/path/to/node",
         "args": ["/path/to/jira-server/build/index.js"],
         "cwd": "/path/to/jira-server",
         "env": {
           "JIRA_HOST": "your-jira-instance.atlassian.net",
           "JIRA_EMAIL": "your-email@example.com",
           "JIRA_API_TOKEN": "your-api-token"
         }
       }
     }
   }
   ```

   Replace `/path/to/jira-server` with the absolute path to your cloned repository.
   Replace `/path/to/node` with the absolute path to your Node.js executable (you can usually find this by running `which node` or `where node` in your terminal).
   Using the direct path to the Node.js executable and the built JavaScript file (`build/index.js` after running `npm run build`) is recommended for reliability.

3. Restart Claude Desktop to apply the changes.

## Configuring Cursor

To use this Jira MCP server with Cursor:

1.  **Ensure the server is built:** Run `npm run build` in the `Jira-MCP-Server` directory to create the necessary `build/index.js` file.
2.  **Locate or create Cursor's MCP configuration file:**
    - For project-specific configuration: `.cursor/mcp.json` in your project's root directory.
    - For global configuration (all projects): `~/.cursor/mcp.json` in your home directory.
3.  **Add the Jira MCP server configuration to `mcp.json`:**

    ```json
    {
      "mcpServers": {
        "jira-mcp-server": {
          "command": "node", // Or provide the absolute path to your Node.js executable
          "args": [
            "/path/to/your/Jira-MCP-Server/build/index.js" // Absolute path to the server's built index.js
          ],
          "cwd": "/path/to/your/Jira-MCP-Server", // Absolute path to the Jira-MCP-Server directory
          "env": {
            "JIRA_HOST": "your-jira-instance.atlassian.net",
            "JIRA_EMAIL": "your-email@example.com", // Your Jira email
            "JIRA_API_TOKEN": "your-api-token" // Your Jira API token
          }
        }
        // You can add other MCP server configurations here
      }
    }
    ```

    - Replace `/path/to/your/Jira-MCP-Server` with the correct absolute path to where you cloned the `Jira-MCP-Server` repository.
    - If `node` is not in your system's PATH or you prefer an absolute path, replace `"node"` with the full path to your Node.js executable (e.g., `/usr/local/bin/node` or `C:\Program Files\nodejs\node.exe`).
    - Ensure your Jira instance details and API token are correctly filled in the `env` section.

4.  **Restart Cursor** to apply the changes.

### Using Cursor Rules for Jira Context

To make interacting with Jira smoother, you can define your default Jira project and user identifier in Cursor's rules. This helps Cursor's AI understand your context without you needing to specify it in every prompt.

Create or edit your Cursor Rules file (e.g., in your project `.cursor/rules.json` or global `~/.cursor/rules.json` (the exact file and method for rules might vary, check Cursor documentation for "Rules" or "Context Management")). Add entries like:

```
As an AI assistant, when I am asked about Jira tasks:
- Assume the primary Jira project key is 'YOUR_PROJECT_KEY_HERE'.
- Assume 'my assigned tasks' or tasks assigned to 'me' refer to the Jira user with the email 'your_jira_email@example.com' (or your Jira Account ID).
You can then use these in your JQL queries, for example: project = YOUR_PROJECT_KEY_HERE AND assignee = 'your_jira_email@example.com'.
```

Replace `YOUR_PROJECT_KEY_HERE` and `your_jira_email@example.com` with your actual details.

### Example Usage in Cursor Chat

Once configured (especially with Cursor Rules for context), you can ask Cursor:

`"Using Jira MCP, list my assigned tasks. Then, based on these tasks, come up with an implementation plan and work schedule."`

If you haven't set up rules, or need to specify a different project or user, you'd be more explicit:

`"Using Jira MCP, list tasks assigned to 'user@example.com' in project 'PROJECT_KEY'. Then, based on these tasks, come up with an implementation plan and work schedule."`

Cursor's AI will use the Jira MCP server to fetch the tasks, and then proceed with the planning and scheduling request.

### Installing via Smithery

To install Jira MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@George5562/Jira-MCP-Server):

```bash
npx -y @smithery/cli install @George5562/Jira-MCP-Server --client claude
```

### Manual Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/George5562/Jira-MCP-Server.git
   cd Jira-MCP-Server
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Configure environment variables:
   Create a `.env` file in the root directory:

   ```bash
   JIRA_HOST=your-instance.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-api-token
   ```

4. Build the project:

   ```bash
   npm run build
   ```

5. Start the server:
   ```bash
   npm start
   ```

## References

- [Model Context Protocol](https://github.com/modelcontextprotocol)
- [Jira REST API Documentation](https://docs.atlassian.com/software/jira/docs/api/REST/7.12.0)
- [Jira REST API Examples](https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/)
