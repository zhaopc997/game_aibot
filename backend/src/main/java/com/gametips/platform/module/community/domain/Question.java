package com.gametips.platform.module.community.domain;

import com.gametips.platform.common.entity.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "question")
public class Question extends BaseEntity {

    @Column(name = "game_id")
    private Long gameId;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "title", nullable = false, length = 255)
    private String title;

    @Column(name = "description")
    private String description;

    @Column(name = "bounty_points", nullable = false)
    private Integer bountyPoints = 0;

    @Column(name = "status", nullable = false, length = 16)
    private String status = "OPEN";

    @Column(name = "accepted_answer_id")
    private Long acceptedAnswerId;
}
