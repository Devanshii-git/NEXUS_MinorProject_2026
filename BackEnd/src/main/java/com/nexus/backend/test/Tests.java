package com.nexus.backend.test;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/tests")
public class Tests {

    @PostMapping("/1")
    public ResponseEntity<?> test1() {

        String val = "Working!! \uD83E\uDD2A";

        return ResponseEntity.ok(Map.of(
            "body", val
        ));
    }

}
