from pathlib import Path

from app.repositories.vector_store_repository import VectorStoreRepository
from app.services.document_service import DocumentService
from app.utils.logger import get_logger
from temporalio import activity
from langchain_core.documents import Document

logger = get_logger(__name__)


def _to_dicts(documents: list[Document]) -> list[dict]:
    return [
        {"page_content": doc.page_content, "metadata": doc.metadata}
        for doc in documents
    ]


def _to_documents(dicts: list[dict]) -> list[Document]:
    return [
        Document(page_content=d["page_content"], metadata=d["metadata"]) for d in dicts
    ]


@activity.defn(name="parse_document_activity")
async def parse_document_activity(local_path: str, filename: str) -> list[dict]:
    activity.logger.info(f"Parsing document from {local_path} with filename {filename}")
    service = DocumentService()

    docs = service.load_file(Path(local_path), source_name=filename)

    return _to_dicts(docs)


@activity.defn(name="chunk_documents_activity")
async def chunk_documents_activity(documents: list[dict]) -> list[dict]:
    activity.logger.info(f"Chunking {len(documents)} documents")

    service = DocumentService()

    chunks = service.split_documents(_to_documents(documents))

    return _to_dicts(chunks)


@activity.defn(name="index_document_activity")
async def index_document_activity(chunks: list[dict]) -> int:
    if not chunks:
        return 0

    repo = VectorStoreRepository()

    ids = repo.add_documents(_to_documents(chunks))

    activity.logger.info(f"Indexed {len(ids)} chunks")

    return len(ids)
