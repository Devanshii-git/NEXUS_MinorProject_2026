package com.nexus.backend.models.mongo;

import com.nexus.backend.models.atlassian.jira.JiraContent;
import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Data
@Document(collection = "comments")
public class Comments {
    @Id
    private CIC_ID id;
    private JiraContent body;     // also ADF format
}
