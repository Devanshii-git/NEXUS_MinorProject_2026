package com.nexus.backend.models;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class UserData {
    private String provider;
    private String id;
    private String name;
    private String email;
    private String avatarUrl;

}
