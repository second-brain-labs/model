from retriever import VespaArticleRetriever
from pathlib import Path
from vespa.application import Vespa
from llama_index import ServiceContext, SimpleDirectoryReader, SummaryIndex
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.response_synthesizers import ResponseMode
from llm import MixtralModalLLM

creds_dir = Path.home() / ".vespa" / "secondbrain.secondbrain.default"
cert_path = creds_dir / "data-plane-public-cert.pem"
key_path = creds_dir / "data-plane-private-key.pem"

VESPA_ENDPOINT = "https://d31b7a33.a4e41a60.z.vespa-app.cloud/"

vespa_app = Vespa(VESPA_ENDPOINT, cert=str(cert_path.absolute()), key=str(key_path.absolute()))

retriever = VespaArticleRetriever(app=vespa_app, user="grohan")
llm = MixtralModalLLM()

service_context = ServiceContext.from_defaults(
    llm=llm, embed_model="local:intfloat/e5-small-v2"
)
query_engine = RetrieverQueryEngine.from_args(
    retriever, service_context=service_context, response_mode=ResponseMode.COMPACT
)
