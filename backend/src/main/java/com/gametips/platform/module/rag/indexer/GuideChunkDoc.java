package com.gametips.platform.module.rag.indexer;

import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.elasticsearch.annotations.Field;
import org.springframework.data.elasticsearch.annotations.FieldType;

import java.util.List;

/**
 * 攻略 chunk 的 ES 文档。
 *
 * 字段 mapping 在 ElasticsearchIndexBootstrap 启动时通过 REST API 主动设置
 * (含 ngram analyzer)。此处注解留 field type 但不再指定 analyzer,
 * 避免 Spring Data ES 试图覆盖我们已经建好的 mapping。
 */
@Data
public class GuideChunkDoc {

    @Id
    private String id;

    @Field(type = FieldType.Long)
    private Long guideId;

    @Field(type = FieldType.Long)
    private Long gameId;

    @Field(type = FieldType.Long)
    private Long versionId;

    @Field(type = FieldType.Text)
    private String title;

    @Field(type = FieldType.Text)
    private String summary;

    @Field(type = FieldType.Text)
    private String text;

    @Field(type = FieldType.Keyword)
    private String status;

    @Field(type = FieldType.Keyword)
    private List<String> tags;

    @Field(type = FieldType.Text)
    private String updatedAt;

    @Field(type = FieldType.Keyword)
    private String sourceUrl;

    @Field(type = FieldType.Dense_Vector, dims = 1024)
    private float[] embedding;
}

