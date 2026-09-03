package com.gametips.platform.module.community.repository;

import com.gametips.platform.module.community.domain.Question;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface QuestionRepository extends JpaRepository<Question, Long> {

    List<Question> findTop50ByGameIdOrderByCreatedAtDesc(Long gameId);
}
