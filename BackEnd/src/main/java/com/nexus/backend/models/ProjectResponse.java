package com.nexus.backend.models;

import lombok.Getter;
import lombok.Setter;

import java.util.Map;

@Getter
@Setter
public class ProjectResponse {
    private String id;
    private String key;
    private String name;
    private String projectTypeKey;  // "software", "business", "service_desk"
    private String style;           // "next-gen" or "classic"
    private boolean simplified;
    private boolean isPrivate;
    private Map<String, String> avatarUrls;
}
