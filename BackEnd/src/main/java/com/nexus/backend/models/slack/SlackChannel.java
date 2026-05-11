package com.nexus.backend.models.slack;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class SlackChannel {
    private String id;
    private String name;
    @JsonProperty("is_member")
    private boolean isMember;
    @JsonProperty("num_members")
    private int numMembers;
}