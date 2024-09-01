from pydantic import BaseModel, computed_field, Field
from asyncio import Task, Queue
from PIL import Image
import asyncio

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
import io

MAX_JOB_AGE = 60 * 60 * 24  # 1 day


class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    status: JobStatus = Field(default=JobStatus.PENDING)
    image: bytes
    result: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None

    @computed_field
    def age(self) -> int:
        if self.completed_at:
            return (datetime.now() - self.completed_at).total_seconds()
        else:
            return (datetime.now() - self.created_at).total_seconds()


job_queue: Queue[UUID] = Queue()
job_results: dict[UUID, Job] = {}
workers: list[Task] = []


async def process_jobs(model, tokenizer, logger):
    while True:
        try:
            # get job from queue. timeout after 1 second
            job_id = await asyncio.wait_for(job_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            continue

        job = job_results.get(job_id, None)
        if not job:
            # job not found in results. this shouldn't happen
            logger.warning(f"Job {job_id} not found")
            job_queue.task_done()  # mark job as done
            continue

        # mark job as processing
        job.status = JobStatus.PROCESSING
        logger.info(f"Processing job {job_id}")

        try:
            # read image from job
            image_bytes = job.image
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            # prepare prompt for model
            question = "What does the text in the image say?"
            msgs = [{"role": "user", "content": [image, question]}]

            # ask model to extract text from image
            result = model.chat(
                image=None,
                msgs=msgs,
                tokenizer=tokenizer,
            )

            # save result and mark job as completed
            job.result = result
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            logger.info(f"Job {job_id} completed successfully")
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            job.status = JobStatus.FAILED
            job.result = str(e)
            job.completed_at = datetime.now()
        finally:
            job_queue.task_done()


async def start_workers(num_workers, model, tokenizer, logger):
    for _ in range(num_workers):
        task = asyncio.create_task(process_jobs(model, tokenizer, logger))
        workers.append(task)

    # Start the periodic cleanup task
    asyncio.create_task(periodic_cleanup(logger))


async def stop_workers():
    for task in workers:
        task.cancel()
    await asyncio.gather(*workers, return_exceptions=True)
    workers.clear()


async def periodic_cleanup(logger):
    while True:
        await asyncio.sleep(3600)  # Run cleanup every hour
        cleanup_jobs(logger)


def cleanup_jobs(logger):
    jobs_to_remove = []

    for job_id, job in job_results.items():
        if job.age > MAX_JOB_AGE:
            jobs_to_remove.append(job_id)

    for job_id in jobs_to_remove:
        del job_results[job_id]
        logger.info(f"Removed expired job {job_id}")

    logger.info(f"Cleanup completed. Removed {len(jobs_to_remove)} expired jobs.")


def get_jobs() -> dict:
    all_jobs = [
        {
            "job_id": str(job.id),
            "status": job.status.value,
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "age": job.age,
        }
        for job in job_results.values()
    ]

    return {
        "total_jobs": len(all_jobs),
        "pending_jobs": [
            job for job in all_jobs if job["status"] == JobStatus.PENDING.value
        ],
        "processing_jobs": [
            job for job in all_jobs if job["status"] == JobStatus.PROCESSING.value
        ],
        "completed_jobs": [
            job for job in all_jobs if job["status"] == JobStatus.COMPLETED.value
        ],
        "failed_jobs": [
            job for job in all_jobs if job["status"] == JobStatus.FAILED.value
        ],
    }
