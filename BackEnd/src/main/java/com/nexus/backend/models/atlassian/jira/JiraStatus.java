package com.nexus.backend.models.atlassian.jira;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class JiraStatus {
    private String id;
    private String name;          // "To Do", "In Progress", "Done"
}