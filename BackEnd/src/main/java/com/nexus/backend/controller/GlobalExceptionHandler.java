package com.nexus.backend.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.client.HttpClientErrorException;

import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(HttpClientErrorException.Forbidden.class)
    public ResponseEntity<?> handleForbidden(HttpClientErrorException.Forbidden e) {
        String body = e.getResponseBodyAsString();

        String provider = "unknown";
        if (body.contains("Tenant is restricted") || body.contains("atlassian")) {
            provider = "atlassian";
        } else if (body.contains("invalid_auth") || body.contains("account_inactive") || body.contains("slack")) {
            provider = "slack";
        }

        return ResponseEntity.status(HttpStatus.FORBIDDEN)
                .body(Map.of(
                        "error", "access_revoked",
                        "provider", provider,
                        "message", switch (provider) {
                            case "atlassian" -> "Your Atlassian workspace access has been revoked or cancelled.";
                            case "slack"     -> "Your Slack workspace access has been revoked.";
                            default          -> "Third-party access has been revoked. Please reconnect.";
                        }
                ));
    }

    @ExceptionHandler(HttpClientErrorException.Unauthorized.class)
    public ResponseEntity<?> handleUnauthorized(HttpClientErrorException.Unauthorized e) {
        String body = e.getResponseBodyAsString();

        String provider = body.contains("atlassian") || body.contains("Unauthorized") ? "atlassian" : "slack";

        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(Map.of(
                        "error", "token_expired",
                        "provider", provider,
                        "message", "Your " + provider + " session has expired. Please log in again."
                ));
    }

    // Catch-all for any other unexpected external API errors
    @ExceptionHandler(HttpClientErrorException.class)
    public ResponseEntity<?> handleOtherClientErrors(HttpClientErrorException e) {
        return ResponseEntity.status(e.getStatusCode())
                .body(Map.of(
                        "error", "external_api_error",
                        "message", "An error occurred with a third-party service.",
                        "detail", e.getResponseBodyAsString()
                ));
    }
}
