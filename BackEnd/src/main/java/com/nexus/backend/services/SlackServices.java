package com.nexus.backend.services;

import com.nexus.backend.models.slack.SlackChannel;
import com.nexus.backend.models.slack.SlackChannelResponse;
import com.nexus.backend.models.slack.SlackMessage;
import com.nexus.backend.models.slack.SlackMessageResponse;
import com.nexus.backend.models.UserData;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.util.List;

@Service
public class SlackServices {

    private final RestClient slackUserRestClient;
    private final RestClient slackBotRestClient;

    public SlackServices(
            @Qualifier("slackRestClient") RestClient slackUserRestClient,
            @Qualifier("slackBotRestClient") RestClient slackBotRestClient
    ) {
        this.slackUserRestClient = slackUserRestClient;
        this.slackBotRestClient = slackBotRestClient;
    }

    public UserData fetchIdentity() {
        return slackUserRestClient.get()
                .uri("https://slack.com/api/users.identity")
                .retrieve()
                .body(UserData.class);
    }

    public List<SlackChannel> fetchChannels() {
        SlackChannelResponse response = slackBotRestClient.get()
                .uri("https://slack.com/api/conversations.list")
                .retrieve()
                .body(SlackChannelResponse.class);

        return response != null && response.isOk() ? response.getChannels() : List.of();
    }

    public List<SlackMessage> fetchMessages(String channelId) {
        SlackMessageResponse response = slackBotRestClient.get()
                .uri("https://slack.com/api/conversations.history?channel=" + channelId)
                .retrieve()
                .body(SlackMessageResponse.class);

        return response != null && response.isOk() ? response.getMessages() : List.of();
    }

}
