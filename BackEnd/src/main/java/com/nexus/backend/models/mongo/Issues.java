package com.nexus.backend.models.mongo;

import com.nexus.backend.models.atlassian.jira.JiraIssueFields;
import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Data
@Document(collection = "issues")
public class Issues {
    @Id
    private CI_ID id;
    private JiraIssueFields fields;

}
