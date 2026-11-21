import asyncio
from pathlib import Path

from app.config.settings import get_settings
from app.repositories.vector_store_repository import VectorStoreRepository
from app.services.document_service import DocumentService
from app.utils.logger import get_logger
from temporalio import activity

logger = get_logger(__name__)


@activity.defn(name="ingest_file_activity")
async def ingest_file_activity(local_path: str, filename: str) -> dict:
    """Parse, chunk and index one file, returning only a small summary.

    Documents and chunks stay inside the activity: passing them between
    activities would store them in workflow history and exceed Temporal's
    payload size limit for large files.
    """
    batch_size = get_settings().index_batch_size
    activity.logger.info(f"Ingesting {filename} from {local_path}")

    service = DocumentService()
    repo = VectorStoreRepository()

    # Blocking work runs in threads so the event loop stays free to heartbeat.
    docs = await asyncio.to_thread(service.load_file, Path(local_path), filename)
    chunks = await asyncio.to_thread(service.split_documents, docs)
    activity.logger.info(f"{filename}: {len(docs)} documents -> {len(chunks)} chunks")

    indexed = 0
    for start in range(0, len(chunks), batch_size):
        ids = await asyncio.to_thread(
            repo.add_documents, chunks[start : start + batch_size]
        )
        indexed += len(ids)
        activity.heartbeat(indexed)

    activity.logger.info(f"Indexed {indexed} chunks for {filename}")
    return {"filename": filename, "chunks_created": indexed}
