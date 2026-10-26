package com.gametips.platform.module.review.event;

import lombok.Getter;

@Getter
public class GuideReviewFinishedEvent {

    private final Long guideId;
    private final String guideTitle;
    private final Long authorId;
    private final boolean passed;
    private final String reason;

    public GuideReviewFinishedEvent(Long guideId, String guideTitle, Long authorId, boolean passed, String reason) {
        this.guideId = guideId;
        this.guideTitle = guideTitle != null ? guideTitle : "";
        this.authorId = authorId;
        this.passed = passed;
        this.reason = reason;
    }
}
