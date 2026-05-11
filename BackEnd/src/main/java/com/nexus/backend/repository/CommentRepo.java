package com.nexus.backend.repository;

import com.nexus.backend.models.mongo.CIC_ID;
import com.nexus.backend.models.mongo.Comments;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface CommentRepo extends MongoRepository<Comments, String> {

    public Comments findById(CIC_ID cicId);

}
