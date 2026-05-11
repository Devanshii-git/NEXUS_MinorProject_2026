package com.nexus.backend.controller;

import com.nexus.backend.models.UserData;
import jakarta.servlet.http.HttpSession;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/user")
public class Logged {

    @GetMapping("/atlassian")
    public UserData atlassianUser(HttpSession session) {
        UserData userData = (UserData) session.getAttribute("atlassian_user");

        if (userData == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Not logged in with Atlassian");
        }

        return userData;
    }

    @GetMapping("/slack")
    public UserData slackUser(HttpSession session) {
        UserData userData = (UserData) session.getAttribute("slack_user");

        if (userData == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Not logged in with Slack");
        }

        return userData;
    }

    @GetMapping("/logged")
    public UserData loggedUser(HttpSession session) {
        UserData atlassian = (UserData) session.getAttribute("atlassian_user");
        if (atlassian != null) return atlassian;

        UserData slack = (UserData) session.getAttribute("slack_user");
        if (slack != null) return slack;

        throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Not logged in");
    }

}
