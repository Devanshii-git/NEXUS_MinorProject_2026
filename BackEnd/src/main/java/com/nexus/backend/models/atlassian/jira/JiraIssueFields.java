package com.nexus.backend.models.atlassian.jira;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class JiraIssueFields {
    private String summary;
    private JiraContent description;   // Jira uses Atlassian Document Format (ADF)
    private JiraUser assignee;
    private JiraUser reporter;
    private JiraStatus status;
    private JiraPriority priority;
    private String created;
    private String updated;
    private JiraCommentPage comment;   // embedded comments
}