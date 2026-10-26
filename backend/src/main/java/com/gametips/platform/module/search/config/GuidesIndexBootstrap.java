package com.gametips.platform.module.search.config;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

import java.io.StringReader;

/**
 * 攻略搜索索引（guides）的显式初始化。
 *
 * <h3>为什么需要</h3>
 * 此前 {@code guides} 索引没有任何初始化代码，靠 <b>ES 动态映射</b>在第一份文档写入时自动创建。
 * 这带来两个问题：
 * <ol>
 *   <li>{@code GuideDocument} 上的 {@code @Field(type = Keyword, analyzer = "ik_max_word")}
 *       等注解<b>完全不生效</b>（索引不是 Spring Data 创建的），实际 mapping 是
 *       dynamic 推断的 text + keyword 多字段 —— 与注解写的完全不一致，极易误导维护者；</li>
 *   <li>mapping 取决于"第一份文档的字段类型"，一旦数据形态变化（例如某游戏返回数字而非字符串），
 *       推断结果可能漂移，进而<b>静默打断搜索</b>（本项目曾因 status 是 text 而 term 查询大写值 0 命中）。</li>
 * </ol>
 *
 * <h3>策略</h3>
 * <b>仅在索引不存在时创建</b>，已存在的索引不做任何改动 ——
 * 避免在线上改 mapping 触发不可逆的字段类型冲突。
 * 同时校验关键字段是否具备 {@code .keyword} 子字段（搜索查询依赖它做精确匹配），
 * 不满足时打 warn 日志，便于提前发现问题而不是等用户反馈"搜不到"。
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class GuidesIndexBootstrap {

    private final ElasticsearchClient client;
    private final SearchProperties properties;

    /**
     * 显式 mapping。
     *
     * <p>与 {@code EsGuideSearchClient} 的查询严格对应：
     * <ul>
     *   <li>{@code status} / {@code tags} 必须是 <b>text + keyword 多字段</b> ——
     *       查询用 {@code status.keyword} 做精确匹配（term 不分析，不能用纯 text）</li>
     *   <li>{@code title} / {@code summary} 为 text，供 multi_match 全文检索</li>
     * </ul>
     */
    private static final String GUIDES_MAPPING = """
            {
              "mappings": {
                "properties": {
                  "id":          { "type": "long" },
                  "gameId":      { "type": "long" },
                  "versionId":   { "type": "long" },
                  "title":       { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
                  "summary":     { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
                  "tags":        { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
                  "difficulty":  { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
                  "status":      { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
                  "likeCount":   { "type": "long" },
                  "usefulCount": { "type": "long" },
                  "updatedAt":   { "type": "date" }
                }
              }
            }
            """;

    @EventListener(ApplicationReadyEvent.class)
    public void ensureGuidesIndex() {
        String index = properties.getElasticsearch().getIndex();
        try {
            boolean exists = client.indices().exists(e -> e.index(index)).value();
            if (exists) {
                log.info("[guides-index] 索引 {} 已存在，跳过创建（不改动已有 mapping）", index);
                return;
            }
            client.indices().create(c -> c
                    .index(index)
                    .withJson(new StringReader(GUIDES_MAPPING)));
            log.info("[guides-index] 已按显式 mapping 创建索引 {}", index);
        } catch (Exception e) {
            // 索引初始化失败不应阻断启动：搜索会降级为空结果，但其它功能应可用
            log.warn("[guides-index] 索引初始化失败（ES 不可用？）: {}", e.getMessage());
        }
    }

}