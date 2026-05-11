package com.nexus.backend.services;

import com.nexus.backend.models.atlassian.AtlassianResource;
import com.nexus.backend.models.atlassian.AtlassianProject;
import com.nexus.backend.models.atlassian.jira.*;
import com.nexus.backend.models.mongo.CIC_ID;
import com.nexus.backend.models.mongo.CI_ID;
import com.nexus.backend.models.mongo.Comments;
import com.nexus.backend.models.mongo.Issues;
import com.nexus.backend.repository.CommentRepo;
import com.nexus.backend.repository.IssueRepo;
import org.jspecify.annotations.NonNull;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.util.UriComponentsBuilder;

import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Service
public class JiraServices {

    private final RestClient restClient;
    private final CommentRepo commentRepo;
    private final IssueRepo issueRepo;

    public JiraServices(@Qualifier("atlassianRestClient") RestClient restClient,  CommentRepo commentRepo,  IssueRepo issueRepo) {
        this.restClient = restClient;
        this.commentRepo = commentRepo;
        this.issueRepo = issueRepo;
    }

    public List<AtlassianResource> fetchAccessibleResources() {
        return restClient.get()
                .uri("https://api.atlassian.com/oauth/token/accessible-resources")
                .retrieve()
                .body(new ParameterizedTypeReference<>() {
                });
    }

    public List<AtlassianProject> fetchProjectInfo(String cloudId) {
        String url = "https://api.atlassian.com/ex/jira/" + cloudId + "/rest/api/3/project";

        return restClient.get()
                .uri(url)
                .retrieve()
                .body(new ParameterizedTypeReference<>() {
                });
    }

    // Fetch all issues in a project
    public JiraIssueSearchResult fetchIssues(String cloudId, String projectKey, int startAt, int maxResult) {

        URI url = UriComponentsBuilder
                .fromUriString("https://api.atlassian.com/ex/jira/" + cloudId + "/rest/api/3/search/jql")
                .queryParam("jql", "project={projectKey}")
                .queryParam("fields", "summary,description,comment,assignee,reporter,status,priority,created,updated")
                .queryParam("maxResults", maxResult)
                .queryParam("startAt", startAt)
                .buildAndExpand(Map.of("projectKey", projectKey)) // handles encoding safely
                .toUri();

        JiraIssueSearchResult dataGot = restClient.get()
                .uri(url)
                .retrieve()
                .body(JiraIssueSearchResult.class);


        if (dataGot == null)
            throw new RuntimeException("Failed to fetch Issues for " + projectKey);

        List<Issues> dataToSave = new ArrayList<>();
        
        for (JiraIssue jiraIssue : dataGot.getIssues()) {
            Issues issue = getIssues(cloudId, jiraIssue.getKey(), jiraIssue.getFields());
            dataToSave.add(issue);
        }
        
        issueRepo.saveAll(dataToSave);

        return dataGot;
    }
    
    private static  @NonNull Issues getIssues(String cloudId, String issueKey, JiraIssueFields fields) {
        CI_ID Id = new CI_ID();
        Id.setCloudId(cloudId);
        Id.setIssueKey(issueKey);
        
        Issues mongoIssue = new Issues();
        mongoIssue.setId(Id);
        mongoIssue.setFields(fields);

        return mongoIssue;
    }

    // Fetch comments for a specific issue
    public JiraCommentPage fetchComments(String cloudId, String issueKey, int startAt, int maxResults) {
        String url = UriComponentsBuilder
                .fromUriString("https://api.atlassian.com/ex/jira/" + cloudId + "/rest/api/3/issue/" + issueKey + "/comment")
                .queryParam("startAt", startAt)
                .queryParam("maxResults", maxResults)
                .toUriString();

        JiraCommentPage dataGot = restClient.get()
                .uri(url)
                .retrieve()
                .body(JiraCommentPage.class);

        if (dataGot == null) {
            throw new RuntimeException("Failed to fetch comments");
        }

        List<Comments> commentsToSave = new ArrayList<>();

        for (JiraComment comment : dataGot.getComments()) {
            Comments mongoComment = getComments(cloudId, issueKey, comment);
            commentsToSave.add(mongoComment);
        }

        commentRepo.saveAll(commentsToSave);

        return dataGot;
    }

    private static @NonNull Comments getComments(String cloudId, String issueKey, JiraComment comment) {
        CIC_ID commentId = new CIC_ID();
        commentId.setCloudId(cloudId);
        commentId.setIssueKey(issueKey);
        commentId.setCommentId(comment.getId());

        Comments mongoComment = new Comments();
        mongoComment.setId(commentId);
        mongoComment.setBody(comment.getBody());

        return mongoComment;
    }
}
