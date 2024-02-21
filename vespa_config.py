from vespa.package import (
    Schema,
    Document,
    Field,
    FieldSet,
    HNSW,
    ApplicationPackage,
    Component,
    Parameter,
    RankProfile,
    Function,
    FirstPhaseRanking,
)
from pathlib import Path

article_schema = Schema(
    name="articles",
    mode="streaming",
    document=Document(
        fields=[
            Field(
                name="article_id",
                type="string",
                indexing=["summary", "attribute"],
                attribute=["fast-search"],
            ),
            Field(
                name="title", type="string", indexing=["summary", "attribute", "index"]
            ),
            Field(name="content", type="string", indexing=["summary", "index"]),
            Field(name="abstract", type="string", indexing=["summary", "index"]),
            Field(name="url", type="string", indexing=["summary", "index"]),
            Field(name="directory", type="string", indexing=["summary"]),
            Field(
                name="embedding",
                type="tensor<bfloat16>(x[384])",
                indexing=[
                    '"passage: " . input title ." ". input content',
                    "embed e5",
                    "attribute",
                    "index",
                ],
                ann=HNSW(distance_metric="angular"),
                is_document_field=False,
            ),
        ],
    ),
    fieldsets=[FieldSet(name="default", fields=["content", "title", "abstract"])],
)


vespa_application_package = ApplicationPackage(
    name="secondbrain",
    schema=[article_schema],
    components=[
        Component(
            id="e5",
            type="hugging-face-embedder",
            parameters=[
                Parameter(
                    "transformer-model",
                    {
                        "url": "https://huggingface.co/intfloat/e5-small-v2/resolve/main/model.onnx"
                    },
                ),
                Parameter(
                    "tokenizer-model",
                    {
                        "url": "https://huggingface.co/intfloat/e5-small-v2/raw/main/tokenizer.json"
                    },
                ),
            ],
        )
    ],
)


semantic_ranking = RankProfile(
    name="semantic",
    functions=[
        Function(name="cosine", expression="max(0,cos(distance(field, embedding)))")
    ],
    inputs=[("query(q)", "tensor<float>(x[384])"), ("query(threshold)", "", "0.75")],
    first_phase=FirstPhaseRanking(
        expression="if(cosine > query(threshold), cosine, -1)",
        rank_score_drop_limit=0.1,
    ),
    match_features=["cosine", "distance(field, embedding)", "query(threshold)"],
)

article_schema.add_rank_profile(semantic_ranking)

if __name__ == "__main__":
    vespa_application_package.to_files(Path("./vespa"))
