# Nexus BackEnd

The core backend service for the Nexus ecosystem, providing Atlassian and Slack integration, OAuth2 authentication, multi-platform project management capabilities, and AI-powered comment and issue analysis.

## 🚀 Features

- **Atlassian Integration**:
  - **OAuth2 Login**: Secure authentication flow using Atlassian's OAuth2 provider.
  - **Jira Management**: Fetch accessible sites, projects, issues, and comments with pagination support.
  - **Comment & Issue Persistence**: Store and manage Jira comments and issues in MongoDB for later retrieval and analysis.
  
- **Slack Integration**:
  - **Channel Access**: Retrieve a list of accessible Slack channels.
  - **Message Retrieval**: Fetch messages from specific channels to sync conversations.
  - **Bot-Level Operations**: Specialized bot token support for advanced Slack operations.
  
- **AI-Powered Features**:
  - **Comment Analysis**: Structure and analyze Jira comments using AI models.
  - **Issue Analysis**: Process multiple issues and extract insights using AI.
  - **Intelligent Processing**: Send comments and issues to AI service for contextual analysis and insights.
  - **Multi-Model Support**: Support for local AI models and LM Studio integration.
  
- **Secure RestClient**: Pre-configured `RestClient` with automatic bearer token injection for third-party API calls.
- **Modern Tech Stack**: Built with Java 21 and Spring Boot 4.0.3.
- **Database Persistence**: MongoDB integration for storing user data, comments, and issues.

## 🛠 Tech Stack

- **Language**: Java 21
- **Framework**: [Spring Boot 4.0.3](https://spring.io/projects/spring-boot)
- **Security**: [Spring Security](https://spring.io/projects/spring-security) (OAuth2 Client)
- **Database**: [Spring Data MongoDB](https://spring.io/projects/spring-data-mongodb)
- **Utilities**: [Lombok](https://projectlombok.org/)
- **Build Tool**: Maven 3.9+
- **Container**: Docker with Amazon Corretto JDK 21

## 📂 Project Structure

```text
src/main/java/com/nexus/backend/
├── config/             # Security, CORS, RestClient configuration, and OAuth2 handlers
├── controller/         # API endpoints (Auth, Jira, Slack, AI)
│   ├── AtlassianController.java
│   ├── SlackController.java
│   ├── AIController.java
│   ├── Logged.java
│   ├── GlobalExceptionHandler.java
│   └── Tests.java
├── models/             # Data models for API responses
│   ├── atlassian/      # Atlassian and Jira models
│   ├── slack/          # Slack models
│   ├── mongo/          # MongoDB document models
│   └── UserData.java
├── services/           # Business logic and external API orchestration
│   ├── JiraServices.java
│   ├── SlackServices.java
│   └── AIService.java
├── repository/         # Data access layer for MongoDB
│   ├── CommentRepo.java
│   └── IssueRepo.java
└── BackEndApplication  # Main Spring Boot entry point
```

## 🛣 API Endpoints

### 👤 User Profile
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/user/atlassian` | Returns the currently authenticated Atlassian user profile (from session). |
| `GET` | `/user/slack` | Returns the currently authenticated Slack user profile (from session). |
| `GET` | `/user/logged` | Returns the currently logged-in user profile (Atlassian or Slack, whichever is authenticated). |

### 🏗 Atlassian / Jira
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/atlassian/resources` | Lists accessible Atlassian resources (sites/cloudIds). |
| `GET` | `/atlassian/projects` | Fetches Jira projects (requires `cloudId`). |
| `GET` | `/atlassian/issues` | Fetches issues for a project with pagination (requires `cloudId`, `projectKey`). Stores issues in MongoDB. |
| `GET` | `/atlassian/comments` | Fetches comments for an issue with pagination (requires `cloudId`, `issueKey`). Stores comments in MongoDB. |

### 💬 Slack
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/slack/channels` | Lists all accessible Slack channels. |
| `GET` | `/slack/channels/{channelId}/messages` | Fetches message history for a specific Slack channel. |

### 🤖 AI Analysis
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/ai/comment-process` | Processes and analyzes selected Jira comments using AI models. |
| `POST` | `/ai/issue-process` | Processes and analyzes selected Jira issues using AI models. |

### 🧪 Testing
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/tests/1` | Health check endpoint to verify API is working. |

## ⚙️ Configuration & Architecture

### 🔐 Security & Auth
The system uses **Spring Security OAuth2 Client** for authentication:
- **Provider Support**: Seamlessly handles both Atlassian and Slack login flows.
- **Success Handling**: `OAuth2LoginSuccessHandler` extracts user metadata (Avatar, Email, IDs) and persists it in the HTTP session as `atlassian_user` or `slack_user`.
- **CORS**: Pre-configured to support cross-origin requests from the Nexus Frontend with support for credentials.
- **Redirection**: Unauthenticated requests are automatically caught and redirected to the frontend login page.
- **Exception Handling**: Global exception handler for graceful error responses with provider-specific messages (access revoked, token expired).

### 🌐 RestClient Interceptors
The project implements a smart `RestClient` architecture to abstract away token management:
- **`atlassianRestClient`**: Automatically injects trailing Atlassian Bearer tokens into outbound requests using an interceptor that talks to the `OAuth2AuthorizedClientManager`.
- **`slackRestClient`**: Handles user-scope message/channel requests with automatic token injection.
- **`slackBotRestClient`**: Specialized client for bot-level operations using the `SLACK_BOT_TOKEN`.
- **`aiRestClient`**: Configured for AI service communication and comment/issue analysis.

### 💾 Database & Persistence
- **MongoDB Integration**: Stores user profiles, comments, and issues.
- **Document Models**: Type-safe models for MongoDB collections:
  - `Comments`: Stores Jira comments with composite ID (CloudID, IssueKey, CommentId)
  - `Issues`: Stores Jira issues with composite ID (CloudID, IssueKey)
- **Repository Layer**: 
  - `CommentRepo`: Provides CRUD operations for comments
  - `IssueRepo`: Provides CRUD operations for issues

### 🔄 Session Management
Authentication state and user profiles are stored in the server-side session. This allows for:
1. Retrieval of user info via the `/user` endpoints.
2. Automatic token refreshing via the `OAuth2AuthorizedClientManager`.
3. Persistent login state across frontend refreshes.
4. Multi-provider support (Atlassian and Slack simultaneously).

### 🤖 AI Service Integration
- **Comment Analysis**: Sends selected Jira comments to AI service for structured analysis.
- **Issue Analysis**: Sends selected Jira issues to AI service for comprehensive analysis.
- **Multi-Model Support**: 
  - **Local Model**: Connects to `http://127.0.0.1:8234/analyze/json` for custom model inference
  - **LM Studio Support**: Alternative endpoint at `http://127.0.0.1:1234/v1/chat/completions` for LM Studio integration using `qwen2.5-coder-7b-instruct` model
- **Payload Structure**: Sends type-tagged payloads with comments/issues body for contextual analysis
- **Context Preservation**: Maintains cloud ID, issue key, and comment IDs during analysis

## 📝 Request/Response Examples

### Fetching Issues with Pagination
```bash
GET /atlassian/issues?cloudId=abc123&projectKey=PROJ&startAt=0&maxResult=50
```

**Response:**
```json
{
  "startAt": 0,
  "maxResults": 50,
  "total": 150,
  "issues": [...]
}
```

### AI Comment Analysis
```bash
POST /ai/comment-process
Content-Type: application/json

{
  "cloudID": "abc123",
  "issueKey": "PROJ-123",
  "commentIds": ["comment1", "comment2"]
}
```

### AI Issue Analysis
```bash
POST /ai/issue-process
Content-Type: application/json

{
  "cloudID": "abc123",
  "issueKeys": ["PROJ-123", "PROJ-124"]
}
```

## 🐳 Deployment

### Docker Support
- **Multi-stage builds**: Optimized production image with minimal dependencies.
- **Base Image**: Amazon Corretto 21 (headless) for production.
- **Build Stage**: Maven 3.9 for dependency resolution and compilation.
- **Port**: Runs on port 8443 (HTTPS).
- **Secrets Management**: Excludes sensitive files (application-secrets.properties, keystore.p12) from Docker image.

### Running the Application
```bash
# Local development
./mvnw spring-boot:run

# Docker build
docker build -t nexus-backend .

# Docker run
docker run -p 8443:8443 nexus-backend
```

## 📋 Query Parameters Reference

### Pagination Parameters
- `startAt` (Integer, default: 0): Starting index for paginated results.
- `maxResult` (Integer, default: 50): Maximum number of results to return.

### Filter Parameters
- `cloudId` (String, required for Jira operations): Atlassian cloud identifier.
- `projectKey` (String, required for project issues): Jira project key (e.g., "PROJ").
- `issueKey` (String, required for issue comments): Jira issue key (e.g., "PROJ-123").
- `channelId` (String/PathVariable, required for Slack messages): Slack channel identifier.

## 🔗 Composite Key Models

### Comments (MongoDB)
```
CloudID + IssueKey + CommentId
```
Stores individual Jira comments with their source context.

### Issues (MongoDB)
```
CloudID + IssueKey
```
Stores Jira issue details including fields (summary, description, assignee, status, etc.).

## 📚 HTTP Status Codes

- `200 OK` - Successfully retrieved data
- `400 BAD REQUEST` - Missing or invalid required parameters
- `401 UNAUTHORIZED` - Not authenticated or session expired
- `403 FORBIDDEN` - Access revoked (workspace or provider revoked permissions)
- `404 NOT FOUND` - Resource not found (project, issue, or channel)
- `500 INTERNAL SERVER ERROR` - Server-side error during processing

---

Developed as part of the **Nexus Project** - Unified Integration Platform for Atlassian and Slack with AI-powered insights and analysis.
