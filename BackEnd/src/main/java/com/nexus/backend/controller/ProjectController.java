package com.nexus.backend.controller;

import com.nexus.backend.models.AtlassianResource;
import com.nexus.backend.models.ProjectResponse;
import com.nexus.backend.services.ProjectService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/atlassian")
public class ProjectController {

    private final ProjectService projectService;

    public ProjectController(ProjectService projectService) {
        this.projectService = projectService;
    }

    @GetMapping("/resources")
    public List<AtlassianResource> getAccessibleResources() {
        return projectService.fetchAccessibleResources();
    }

    @GetMapping("/projects")
    public List<ProjectResponse> getProjectInfo(@RequestParam String cloudId) {
        return projectService.fetchProjectInfo(cloudId);
    }
}