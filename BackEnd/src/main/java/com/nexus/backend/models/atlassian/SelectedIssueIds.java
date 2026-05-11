package com.nexus.backend.models.atlassian;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
public class SelectedIssueIds {
    private String cloudID;
    private List<String> issueKeys;
}
