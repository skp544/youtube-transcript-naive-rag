from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from app.temporal.activities.ingestion import ingest_file_activity

DEFAULT_INDEX_BATCH_SIZE = 100


@dataclass
class FileIngestInput:
    filename: str
    local_path: str


@dataclass
class BatchIngestProgress:
    status: str = "RUNNING"
    files_total: int = 0
    files_completed: int = 0
    current_filename: str | None = None
    file_results: list[dict[str, Any]] = field(default_factory=list)


@workflow.defn(name="batch-ingestion-workflow")
class BatchIngestionWorkflow:
    """Workflow to ingest of files into the vector store."""

    def __init__(self) -> None:
        self.progress = BatchIngestProgress()

    @workflow.query
    def get_progress(self) -> BatchIngestProgress:
        return self.progress

    @workflow.run
    async def run(self, files: list[FileIngestInput]) -> BatchIngestProgress:
        """Workflow to ingest a batch of files into the new vector store"""

        self.progress.files_total = len(files)
        self.progress.status = "RUNNING"
        batch_size = DEFAULT_INDEX_BATCH_SIZE

        for file_input in files:
            self.progress.current_filename = file_input.filename

            indexed = await workflow.execute_activity(
                ingest_file_activity,
                args=[file_input.local_path, file_input.filename, batch_size],
                start_to_close_timeout=timedelta(minutes=60),
                heartbeat_timeout=timedelta(minutes=5),
            )

            # result = await workflow.execute_activity(
            #     ingest_file_activity,
            #     args=[file_input.local_path, file_input.filename],
            #     start_to_close_timeout=timedelta(hours=2),
            #     heartbeat_timeout=timedelta(minutes=5),
            # )

            self.progress.files_completed += 1
            self.progress.file_results.append(
                {
                    "filename": file_input.filename,
                    "chunks_created": indexed,
                    "document_ids": [],
                }
            )

        self.progress.status = "COMPLETED"
        self.progress.current_filename = None
        return self.progress
