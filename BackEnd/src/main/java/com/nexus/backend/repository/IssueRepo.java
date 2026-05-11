package com.nexus.backend.repository;

import com.nexus.backend.models.mongo.CI_ID;
import com.nexus.backend.models.mongo.Issues;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface IssueRepo extends MongoRepository<Issues, String> {
    public Issues findById(CI_ID ciId);
}
