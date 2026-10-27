package com.gametips.platform.module.community.domain;

import com.gametips.platform.common.entity.BaseEntity;
import com.gametips.platform.common.validation.NoHtml;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import jakarta.validation.constraints.Size;
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
    @NoHtml
    @Size(max = 200, message = "标题最多 200 字")
    private String title;

    @Column(name = "description")
    @NoHtml
    @Size(max = 5000, message = "描述最多 5000 字")
    private String description;

    @Column(name = "bounty_points", nullable = false)
    private Integer bountyPoints = 0;

    @Column(name = "status", nullable = false, length = 16)
    private String status = "OPEN";

    @Column(name = "accepted_answer_id")
    private Long acceptedAnswerId;
}
