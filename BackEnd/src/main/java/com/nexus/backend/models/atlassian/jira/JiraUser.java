package com.nexus.backend.models.atlassian.jira;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class JiraUser {
    private String accountId;
    private String displayName;
    private String emailAddress;
    private String avatarUrl;
}