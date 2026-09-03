package com.gametips.platform.module.ai.domain;

import com.gametips.platform.common.entity.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@Entity
@Table(name = "ai_parse_task")
public class AiParseTask extends BaseEntity {

    @Column(name = "source_url")
    private String sourceUrl;

    @Column(name = "source_type", nullable = false, length = 32)
    private String sourceType;

    @Column(name = "source_hash", nullable = false, length = 64, unique = true)
    private String sourceHash;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 32)
    private AiTaskStatus status = AiTaskStatus.PENDING;

    @Column(name = "result_guide_id")
    private Long resultGuideId;

    @Column(name = "error_msg")
    private String errorMsg;
}
