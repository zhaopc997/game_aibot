package com.gametips.platform;

import com.gametips.platform.common.api.ApiResponse;
import com.gametips.platform.common.api.BizException;
import com.gametips.platform.common.api.ErrorCodes;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class ApiResponseTest {

    @Test
    void ok_shouldReturnSuccessCode() {
        ApiResponse<String> resp = ApiResponse.ok("data");
        assertThat(resp.getCode()).isEqualTo(0);
        assertThat(resp.getMessage()).isEqualTo("success");
        assertThat(resp.getData()).isEqualTo("data");
    }

    @Test
    void error_shouldCarryCodeAndMessage() {
        ApiResponse<Void> resp = ApiResponse.error(ErrorCodes.NOT_FOUND, "攻略不存在");
        assertThat(resp.getCode()).isEqualTo(2001);
        assertThat(resp.getData()).isNull();
    }

    @Test
    void bizException_shouldExposeCode() {
        BizException e = new BizException(ErrorCodes.CONFLICT, "用户名已存在");
        assertThat(e.getCode()).isEqualTo(2002);
        assertThat(e.getMessage()).isEqualTo("用户名已存在");
        assertThatThrownBy(() -> { throw e; })
                .isInstanceOf(BizException.class);
    }
}
