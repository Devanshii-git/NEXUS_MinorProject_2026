package com.nexus.backend.models.atlassian.jira;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;

import java.util.List;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class JiraContentNode {
    private String type;          // "paragraph", "text", "heading" etc.
    private String text;
    private List<JiraContentNode> content;   // nested nodes
}