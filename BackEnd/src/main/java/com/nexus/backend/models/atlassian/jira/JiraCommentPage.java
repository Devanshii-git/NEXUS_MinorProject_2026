package com.nexus.backend.models.atlassian.jira;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;

import java.util.List;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class JiraCommentPage {
    private int total;
    private int startAt;
    private int maxResults;
    private List<JiraComment> comments;
}