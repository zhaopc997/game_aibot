# RAG Design

> 状态：检索链路已实现并可运行；精排（rerank）与按 step 切块尚未落地。
> 权威设计见 `docs/architecture/architecture-v2.md` §4.4-4.6。

## Pipeline

```
Game Data
 |
Document Split        (当前：1 篇攻略 = 1 chunk，未做长文切分)
 |
Embedding             (SiliconFlow 云端 bge-m3，1024 维；未配置 key 时降级为纯 BM25)
 |
Vector Store          (Elasticsearch 8，索引 guide_chunks)
 |
Retriever             (BM25 + KNN 混合检索)
 |                      ├─ BM25：multi_match，title^3 + text^2 + summary
 |                      └─ KNN ：dense_vector cosine，依赖 embedding
 |                   RRF 融合：score = Σ 1/(60 + rank)
 |
LLM                   (Agent 拼装 context 后调用 chat/completions)
```

## 已落地

- **索引写入**：事件驱动增量 + `/api/v1/rag/reindex` 手动重建
- **中文分词**：ngram 2-3（标准 ES 镜像不带 ik，属有意降级）
- **混合检索**：标准 RRF（Reciprocal Rank Fusion），按名次加权而非原始分数，
  避免 BM25(无上界) 与 KNN 余弦(0-1) 分数语义不一致时相互压制
- **候选池放大**：融合前每路召回 `topK * 5`，保证 KNN 有机会贡献结果
  （若两路都只取 topK，BM25 会吃满名额使 KNN 永不生效）
- **降级链**：embedding key 缺失 → 跳过 KNN 走纯 BM25；异常 → 返回空并标记 degraded

## 未落地（与技术选型文档的差异）

| 项 | 文档设计 | 当前实现 |
|---|---|---|
| 文档切分 | 按 step 切分，长文多 chunk | 整篇 1 chunk；已索引 step.title **与 step.description**（单步上限 600 字） |
| 召回量 | BM25 / KNN 各 Top-50 | `topK=5`，候选池 25（`app.rag.top-k` 可调） |
| 精排 | BGE Reranker Top-10 | **未实现**，无 RerankService / 无相关配置 |
| 嵌入位置 | 本地 bge-m3 优先 | 云端 SiliconFlow（`app.rag.embedding.base-url` 可改） |
| 版本过滤 | 按 version 强过滤 | `RagQuery.versionId` 字段已定义但**尚未在检索中生效** |

> 注：`app.rag.use-bm25` 配置项已定义但当前未被读取，纯 BM25 降级由
> `embeddingClient.isEnabled()` 决定。