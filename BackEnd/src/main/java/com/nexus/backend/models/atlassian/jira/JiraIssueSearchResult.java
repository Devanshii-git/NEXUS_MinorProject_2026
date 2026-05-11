package com.nexus.backend.models.atlassian.jira;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;

import java.util.List;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class JiraIssueSearchResult {
    private int total;
    private int startAt;
    private int maxResults;
    private List<JiraIssue> issues;
}
