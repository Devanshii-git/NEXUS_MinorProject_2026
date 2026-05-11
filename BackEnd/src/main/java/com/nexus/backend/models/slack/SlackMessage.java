package com.nexus.backend.models.slack;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class SlackMessage {
    private String type;
    private String text;
    private String user;
    private String ts;
}
