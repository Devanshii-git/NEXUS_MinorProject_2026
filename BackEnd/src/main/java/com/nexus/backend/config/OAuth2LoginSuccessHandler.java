package com.nexus.backend.config;

import com.nexus.backend.models.UserData;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import org.jspecify.annotations.NonNull;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.client.OAuth2AuthorizedClient;
import org.springframework.security.oauth2.client.OAuth2AuthorizedClientService;
import org.springframework.security.oauth2.client.authentication.OAuth2AuthenticationToken;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;

@Component
public class OAuth2LoginSuccessHandler implements AuthenticationSuccessHandler {

    private final String FRONT_END = "https://localhost:5173";
    private final OAuth2AuthorizedClientService authorizedClientService;

    public OAuth2LoginSuccessHandler(OAuth2AuthorizedClientService authorizedClientService) {
        this.authorizedClientService = authorizedClientService;
    }

    @Override
    public void onAuthenticationSuccess(HttpServletRequest request,
                                        @NonNull HttpServletResponse response,
                                        Authentication authentication) throws IOException {

        OAuth2AuthenticationToken token = (OAuth2AuthenticationToken) authentication;
        OAuth2User oAuth2User = token.getPrincipal();
        String provider = token.getAuthorizedClientRegistrationId(); // "atlassian" or "slack"

        OAuth2AuthorizedClient client = authorizedClientService.loadAuthorizedClient(
                provider, authentication.getName());

        if (provider.equals("atlassian")) {

        }

        // Build your UserData object from OAuth2User attributes
        UserData userData = new UserData();
        userData.setName(oAuth2User.getAttribute("name"));
        userData.setEmail(oAuth2User.getAttribute("email"));
        userData.setProvider(provider);

// picture works for both Atlassian (picture) and Slack OIDC (picture)
        userData.setAvatarUrl(oAuth2User.getAttribute("picture"));

// Atlassian uses account_id, Slack OIDC uses sub
        if (oAuth2User.getAttribute("account_id") != null)
            userData.setId(oAuth2User.getAttribute("account_id"));
        else
            userData.setId(oAuth2User.getAttribute("sub"));


        // Save into session based on provider
        HttpSession session = request.getSession();
        if ("atlassian".equals(provider)) {
            session.setAttribute("atlassian_user", userData);
        } else if ("slack".equals(provider)) {
            session.setAttribute("slack_user", userData);
        }

//        System.out.println("Provider: " + provider);
//        System.out.println("Attributes: " + oAuth2User.getAttributes());

//        response.sendRedirect("/user/" + provider);
        response.sendRedirect(FRONT_END);
    }
}