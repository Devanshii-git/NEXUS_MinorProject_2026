package com.nexus.backend.models;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
public class AtlassianResource {
    private String id;
    private String name;
    private String url;
    private List<String> scopes;
    private String avatarUrl;
}