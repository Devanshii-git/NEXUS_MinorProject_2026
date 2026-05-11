package com.nexus.backend.models.atlassian;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
public class SelectedCommentsIds {
    private String cloudID;
    private String issueKey;
    private List<String> commentIds;
}
