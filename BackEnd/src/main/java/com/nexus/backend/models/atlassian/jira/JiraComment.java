package com.nexus.backend.models.atlassian.jira;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.mongodb.lang.Nullable;
import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class JiraComment {

    private String id;
    private JiraUser author;
    private JiraContent body;     // also ADF format
    private String created;
    private String updated;
}