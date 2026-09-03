package com.gametips.platform.module.community.repository;

import com.gametips.platform.module.community.domain.Answer;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface AnswerRepository extends JpaRepository<Answer, Long> {

    List<Answer> findByQuestionIdOrderByCreatedAtAsc(Long questionId);
}
