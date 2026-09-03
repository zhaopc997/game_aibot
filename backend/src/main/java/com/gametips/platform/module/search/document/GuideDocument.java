package com.gametips.platform.module.search.document;

import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.elasticsearch.annotations.Document;
import org.springframework.data.elasticsearch.annotations.Field;
import org.springframework.data.elasticsearch.annotations.FieldType;
import org.springframework.data.elasticsearch.annotations.Setting;

import java.time.Instant;
import java.util.List;

/**
 * 攻略搜索文档（Elasticsearch 索引）。
 */
@Data
@Document(indexName = "guides")
@Setting(settingPath = "elasticsearch/guide-settings.json")
public class GuideDocument {

    @Id
    private Long id;

    @Field(type = FieldType.Long)
    private Long gameId;

    @Field(type = FieldType.Long)
    private Long versionId;

    @Field(type = FieldType.Text, analyzer = "ik_max_word", searchAnalyzer = "ik_smart")
    private String title;

    @Field(type = FieldType.Text, analyzer = "ik_max_word", searchAnalyzer = "ik_smart")
    private String summary;

    @Field(type = FieldType.Keyword)
    private List<String> tags;

    @Field(type = FieldType.Keyword)
    private String difficulty;

    @Field(type = FieldType.Keyword)
    private String status;

    @Field(type = FieldType.Long)
    private Long likeCount;

    @Field(type = FieldType.Long)
    private Long usefulCount;

    @Field(type = FieldType.Date)
    private Instant updatedAt;
}
