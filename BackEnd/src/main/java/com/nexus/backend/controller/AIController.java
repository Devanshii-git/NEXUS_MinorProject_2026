package com.nexus.backend.controller;

import com.nexus.backend.models.atlassian.SelectedCommentsIds;
import com.nexus.backend.models.atlassian.SelectedIssueIds;
import com.nexus.backend.services.AIService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;


@RestController
@RequestMapping("/ai")
public class AIController {

    AIService aiService;

    public AIController(AIService aiService) {
        this.aiService = aiService;
    }

    @PostMapping("/comment-process")
    public ResponseEntity<?> getSelectedComments(
            @RequestBody SelectedCommentsIds selectedCommentsIds
    ){
        return aiService.commentStructurer(selectedCommentsIds);
    }

    @PostMapping("/issue-process")
    public ResponseEntity<?> getSelectedIssues(
            @RequestBody SelectedIssueIds selectedIssueIds
            ){
        return aiService.issueStructurer(selectedIssueIds);
    }


}
