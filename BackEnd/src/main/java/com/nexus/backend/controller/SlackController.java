package com.nexus.backend.controller;

import com.nexus.backend.models.slack.SlackChannel;
import com.nexus.backend.models.slack.SlackMessage;
import com.nexus.backend.services.SlackServices;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/slack")
public class SlackController {

    private final SlackServices slackServices;

    public SlackController(SlackServices slackServices) {
        this.slackServices = slackServices;
    }

    @GetMapping("/channels")
    public List<SlackChannel> getChannels() {
        return slackServices.fetchChannels();
    }

    @GetMapping("/channels/{channelId}/messages")
    public List<SlackMessage> getMessages(@PathVariable String channelId) {
        return slackServices.fetchMessages(channelId);
    }

}
