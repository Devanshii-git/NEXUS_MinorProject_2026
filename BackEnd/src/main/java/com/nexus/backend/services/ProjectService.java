package com.nexus.backend.services;

import com.nexus.backend.models.AtlassianResource;
import com.nexus.backend.models.ProjectResponse;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.util.List;

@Service
public class ProjectService {

    private final RestClient restClient;

    public ProjectService(RestClient restClient) {
        this.restClient = restClient;
    }

    public List<AtlassianResource> fetchAccessibleResources() {
        return restClient.get()
                .uri("https://api.atlassian.com/oauth/token/accessible-resources")
                .retrieve()
                .body(new ParameterizedTypeReference<List<AtlassianResource>>() {});
    }

    public List<ProjectResponse> fetchProjectInfo(String cloudId) {
        String url = "https://api.atlassian.com/ex/jira/" + cloudId + "/rest/api/3/project";

        return restClient.get()
                .uri(url)
                .retrieve()
                .body(new ParameterizedTypeReference<List<ProjectResponse>>() {});
    }
}
