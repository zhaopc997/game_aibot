package com.gametips.platform;

import com.gametips.platform.module.content.domain.Guide;
import com.gametips.platform.module.content.domain.GuideStatus;
import com.gametips.platform.module.content.service.GuideSearchService;
import com.gametips.platform.module.content.service.GuideService;
import com.gametips.platform.module.content.web.GuideController;
import com.gametips.platform.module.version.domain.Game;
import com.gametips.platform.module.version.service.GameService;
import com.gametips.platform.module.version.web.GameController;
import org.junit.jupiter.api.Test;
import org.springframework.data.domain.PageImpl;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

class HomeControllerTest {

    @Test
    void shouldReturnGamesAndGuidesSuccessfully() throws Exception {
        GameService gameService = mock(GameService.class);
        Game g = new Game();
        g.setName("原神");
        g.setCategory("开放世界");
        when(gameService.listAll()).thenReturn(List.of(g));

        GameController gameController = new GameController(gameService);
        MockMvc gameMvc = MockMvcBuilders.standaloneSetup(gameController).build();

        gameMvc.perform(get("/api/v1/games"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data[0].name").value("原神"));

        GuideService guideService = mock(GuideService.class);
        GuideSearchService searchService = mock(GuideSearchService.class);
        Guide guide = new Guide();
        guide.setTitle("钟离培养指南");
        guide.setStatus(GuideStatus.PUBLISHED);
        when(guideService.listByGame(any(), eq(GuideStatus.PUBLISHED), anyInt(), anyInt()))
                .thenReturn(new PageImpl<>(List.of(guide)));

        GuideController guideController = new GuideController(guideService, searchService);
        MockMvc guideMvc = MockMvcBuilders.standaloneSetup(guideController).build();

        guideMvc.perform(get("/api/v1/guides?status=PUBLISHED&size=6"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.items[0].title").value("钟离培养指南"));
    }
}
