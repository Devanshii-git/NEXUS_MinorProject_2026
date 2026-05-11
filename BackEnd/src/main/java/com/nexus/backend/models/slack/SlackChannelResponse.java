package com.nexus.backend.models.slack;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
public class SlackChannelResponse {
    private boolean ok;
    private List<SlackChannel> channels;
}
