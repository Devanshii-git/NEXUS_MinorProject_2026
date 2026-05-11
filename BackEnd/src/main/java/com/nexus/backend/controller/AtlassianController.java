package com.nexus.backend.controller;

import com.nexus.backend.models.atlassian.AtlassianResource;
import com.nexus.backend.models.atlassian.AtlassianProject;
import com.nexus.backend.models.atlassian.SelectedCommentsIds;
import com.nexus.backend.models.atlassian.jira.JiraCommentPage;
import com.nexus.backend.models.atlassian.jira.JiraIssueSearchResult;
import com.nexus.backend.services.JiraServices;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/atlassian")
public class AtlassianController {

    private final JiraServices jiraService;

    public AtlassianController(JiraServices jiraService) {
        this.jiraService = jiraService;
    }

    @GetMapping("/resources")
    public List<AtlassianResource> getAccessibleResources() {
        return jiraService.fetchAccessibleResources();
    }

    @GetMapping("/projects")
    public List<AtlassianProject> getProjectInfo(@RequestParam String cloudId) {
        return jiraService.fetchProjectInfo(cloudId);
    }

    @GetMapping("/issues")
    public JiraIssueSearchResult getIssues(
            @RequestParam String cloudId,
            @RequestParam String projectKey,
            @RequestParam(defaultValue = "0") int startAt,
            @RequestParam(defaultValue = "50") int maxResult
            ) {
        return jiraService.fetchIssues(cloudId, projectKey, startAt, maxResult);
    }

    @GetMapping("/comments")
    public JiraCommentPage getComments(
            @RequestParam String cloudId,
            @RequestParam String issueKey,
            @RequestParam(defaultValue = "0") int startAt,
            @RequestParam(defaultValue = "50") int maxResult
    ) {
        return jiraService.fetchComments(cloudId, issueKey, startAt, maxResult);
    }

//    @PostMapping("/selected-commemts")
//    public ResponseEntity<?> getSelectedComments(
//            @RequestParam SelectedCommentsIds selectedCommentsIds
//    ){
//        System.out.println(selectedCommentsIds);
//
//        return ResponseEntity.ok("data received");
//    }
}