package com.nexus.backend.services;

import com.nexus.backend.models.atlassian.SelectedCommentsIds;
import com.nexus.backend.models.atlassian.SelectedIssueIds;
import com.nexus.backend.models.atlassian.jira.JiraContent;
import com.nexus.backend.models.atlassian.jira.JiraContentNode;
import com.nexus.backend.models.atlassian.jira.JiraIssueFields;
import com.nexus.backend.models.mongo.CIC_ID;
import com.nexus.backend.models.mongo.CI_ID;
import com.nexus.backend.models.mongo.Comments;
import com.nexus.backend.models.mongo.Issues;
import com.nexus.backend.repository.CommentRepo;
import com.nexus.backend.repository.IssueRepo;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;
import tools.jackson.databind.ObjectMapper;

import java.net.URI;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class AIService {

    RestClient restClient;
    CommentRepo commentRepo;
    IssueRepo issueRepo;

    public AIService(@Qualifier("aiRestClient") RestClient restClient, CommentRepo commentRepo,  IssueRepo issueRepo) {
        this.commentRepo = commentRepo;
        this.restClient = restClient;
        this.issueRepo = issueRepo;
    }

    public ResponseEntity<?> issueStructurer(SelectedIssueIds selectedIssueIds) {
        String cloudID = selectedIssueIds.getCloudID();
        List<String> issueKeys = selectedIssueIds.getIssueKeys();

        List<Issues> issues = new ArrayList<>();
        for (String issueKey : issueKeys) {
            CI_ID ciId = new CI_ID();
            ciId.setCloudId(cloudID);
            ciId.setIssueKey(issueKey);
            issues.add(issueRepo.findById(ciId));
        }

        return aiResponse(issues);
//        return lmAiResponse(issues);
    }

    public ResponseEntity<?> commentStructurer(SelectedCommentsIds selectedCommentsIds){
        String cloudID = selectedCommentsIds.getCloudID();
        String issueKey = selectedCommentsIds.getIssueKey();
        List<String> commentIds = selectedCommentsIds.getCommentIds();

        CIC_ID cicId = new CIC_ID();
        cicId.setCloudId(cloudID);
        cicId.setIssueKey(issueKey);

        List<Comments> comments = new ArrayList<>();

        for (String commentId : commentIds) {
            cicId.setCommentId(commentId);
            comments.add(commentRepo.findById(cicId));
        }
//        System.out.println(comments);

        return aiResponse(comments);
//        return lmAiResponse(comments);
    }

    private <T> ResponseEntity<?> aiResponse(List<T> items) {
        URI uri = UriComponentsBuilder
                .fromUriString("http://127.0.0.1:8234/analyze/json")
                .build()
                .toUri();

        List<Map<String, String>> payloadList = items.stream()
                .map(item -> {
                    if (item instanceof Comments comment) {
                        return Map.of(
                                "type", "comments",
                                "body", comment.getBody().toString()
                        );
                    } else if (item instanceof Issues issue) {
                        return Map.of(
                                "type", "issues",
                                "body", buildIssueText(issue)
                        );
                    }
                    throw new IllegalArgumentException("Unsupported type: " + item.getClass().getName());
                })
                .collect(Collectors.toList());

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("model", "local-model");
        requestBody.put("payload", payloadList);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

        RestTemplate restTemplate = new RestTemplate();
        ResponseEntity<String> response = restTemplate.postForEntity(uri, entity, String.class);

        return ResponseEntity.ok(response.getBody());
    }

    private <T> ResponseEntity<?> lmAiResponse(List<T> items) {
        URI uri = UriComponentsBuilder
                .fromUriString("http://127.0.0.1:1234/v1/chat/completions")
                .build()
                .toUri();

        List<Map<String, String>> payloadList = items.stream()
                .map(item -> {
                    if (item instanceof Comments comment) {
                        return Map.of(
                                "type", "comments",
                                "body", comment.getBody().toString()
                        );
                    } else if (item instanceof Issues issue) {
                        return Map.of(
                                "type", "issues",
                                "body", issue.getFields().toString()
                        );
                    }
                    throw new IllegalArgumentException("Unsupported type: " + item.getClass().getName());
                })
                .collect(Collectors.toList());

        // Serialize payload to JSON string
        String payloadJson;
        try {
            ObjectMapper mapper = new ObjectMapper();
            payloadJson = mapper.writeValueAsString(payloadList);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body("Failed to serialize payload: " + e.getMessage());
        }

        // LM Studio chat format
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("model", "nvidia/nemotron-3-nano-4b");
        requestBody.put("messages", List.of(
                Map.of("role", "user", "content", payloadJson)
        ));

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

        RestTemplate restTemplate = new RestTemplate();
        ResponseEntity<String> response = restTemplate.postForEntity(uri, entity, String.class);

        return ResponseEntity.ok(response.getBody());
    }


    private String buildIssueText(Issues issue) {
        JiraIssueFields fields = issue.getFields();
        StringBuilder sb = new StringBuilder();

        // Summary — core requirement text
        if (fields.getSummary() != null)
            sb.append(fields.getSummary()).append(". ");

        // Description (ADF)
        if (fields.getDescription() != null) {
            String desc = extractAdfText(fields.getDescription());
            if (!desc.isBlank())
                sb.append(desc).append(". ");
        }

        // Comments only — skip priority/status/assignee
        // (these are metadata, not requirements)
        if (fields.getComment() != null && fields.getComment().getComments() != null) {
            fields.getComment().getComments().forEach(comment -> {
                String commentText = extractAdfText(comment.getBody());
                if (!commentText.isBlank())
                    sb.append(commentText).append(". ");
            });
        }

        return sb.toString().trim();
    }
    private String extractAdfText(JiraContent node) {
        if (node == null || node.getContent() == null) return "";
        StringBuilder sb = new StringBuilder();
        for (JiraContentNode child : node.getContent()) {
            extractNodeText(child, sb);
        }
        return sb.toString().trim();
    }

    private void extractNodeText(JiraContentNode node, StringBuilder sb) {
        if (node == null) return;
        // Leaf text node
        if (node.getText() != null)
            sb.append(node.getText()).append(" ");
        // Recurse into children
        if (node.getContent() != null)
            node.getContent().forEach(child -> extractNodeText(child, sb));
    }

}
