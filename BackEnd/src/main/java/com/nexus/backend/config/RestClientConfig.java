package com.nexus.backend.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.oauth2.client.OAuth2AuthorizedClientManager;
import org.springframework.security.oauth2.client.OAuth2AuthorizedClientProviderBuilder;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.web.DefaultOAuth2AuthorizedClientManager;
import org.springframework.security.oauth2.client.web.OAuth2AuthorizedClientRepository;
import org.springframework.web.client.RestClient;
import org.springframework.http.client.ClientHttpRequestInterceptor;
import org.springframework.security.oauth2.client.OAuth2AuthorizeRequest;
import org.springframework.security.oauth2.client.OAuth2AuthorizedClient;
import org.springframework.beans.factory.annotation.Value;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@Configuration
public class RestClientConfig {

    @Bean
    public OAuth2AuthorizedClientManager authorizedClientManager(
            ClientRegistrationRepository clientRegistrationRepository,
            OAuth2AuthorizedClientRepository authorizedClientRepository) {

        DefaultOAuth2AuthorizedClientManager manager = new DefaultOAuth2AuthorizedClientManager(
                clientRegistrationRepository, authorizedClientRepository);

        manager.setAuthorizedClientProvider(
                OAuth2AuthorizedClientProviderBuilder.builder()
                        .authorizationCode()
                        .refreshToken()
                        .build());

        return manager;
    }

    // Atlassian specific RestClient
    @Bean(name = "atlassianRestClient")
    public RestClient atlassianRestClient(OAuth2AuthorizedClientManager authorizedClientManager) {
        return buildRestClient("atlassian", authorizedClientManager);
    }

    // Slack specific RestClient
    @Bean(name = "slackRestClient")
    public RestClient slackRestClient(OAuth2AuthorizedClientManager authorizedClientManager) {
        return buildRestClient("slack", authorizedClientManager);
    }

    @Bean(name = "slackBotRestClient")
    public RestClient slackBotRestClient(@Value("${SLACK_BOT_TOKEN}") String botToken) {
        return RestClient.builder()
                .defaultHeader("Authorization", "Bearer " + botToken)
                .build();
    }

    @Bean(name = "aiRestClient")
    public RestClient aiRestClient() {
        return RestClient.builder()
                .baseUrl("http://127.0.0.1:1234")
                .defaultHeader("Content-Type", "application/json")
                .build();
    }

    private RestClient buildRestClient(String provider, OAuth2AuthorizedClientManager authorizedClientManager) {
        ClientHttpRequestInterceptor interceptor = (request, body, execution) -> {
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

            if (authentication == null) {
                throw new IllegalStateException("No authentication found");
            }

            ServletRequestAttributes attrs =
                    (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();

            OAuth2AuthorizeRequest authorizeRequest = OAuth2AuthorizeRequest
                    .withClientRegistrationId(provider)
                    .principal(authentication)
                    .attributes(a -> {
                        a.put(HttpServletRequest.class.getName(), attrs.getRequest());
                        a.put(HttpServletResponse.class.getName(), attrs.getResponse());
                    })
                    .build();

            OAuth2AuthorizedClient authorizedClient =
                    authorizedClientManager.authorize(authorizeRequest);

            if (authorizedClient != null) {
                request.getHeaders().setBearerAuth(
                        authorizedClient.getAccessToken().getTokenValue());
            }

            return execution.execute(request, body);
        };

        return RestClient.builder()
                .requestInterceptor(interceptor)
                .build();
    }
}