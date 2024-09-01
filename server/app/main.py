from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from contextlib import asynccontextmanager
from uuid import UUID
import asyncio

from app.jobs import job_queue, job_results, start_workers, stop_workers, Job, JobStatus
from app.deps import get_model, get_tokenizer
from app.logging import setup_logger

logger = setup_logger()


async def admin_only():
    # This is a placeholder for actual admin authentication
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    # load model and tokenizer
    app.state.model = await get_model()
    app.state.tokenizer = await get_tokenizer()

    # start background task for processing jobs
    asyncio.create_task(
        start_workers(
            num_workers=4,
            model=app.state.model,
            tokenizer=app.state.tokenizer,
            logger=logger,
        )
    )

    yield

    # clean up resources
    await stop_workers()


app = FastAPI(
    title="VLM OCR API",
    description="API for OCR using Vision Language Model",
    version="0.1.0",
    lifespan=lifespan,
)


@app.post("/ocr")
async def create_ocr_job(file: UploadFile = File(...)) -> dict:
    job = Job(image=await file.read())
    job_results[job.id] = job
    await job_queue.put(job.id)
    logger.info(f"New OCR job created with ID: {job.id}")
    return {"job_id": str(job.id)}


@app.get("/ocr/{job_id}")
async def get_ocr_job(job_id: UUID) -> dict:
    if job_id not in job_results:
        logger.warning(f"Job not found: {job_id}")
        raise HTTPException(status_code=404, detail="Job not found")

    job = job_results[job_id]
    if job.status == JobStatus.COMPLETED:
        return {"status": job.status.value, "result": job.result}
    elif job.status == JobStatus.FAILED:
        return {"status": job.status.value, "error": job.result}
    else:
        return {"status": job.status.value}


@app.get("/admin/jobs")
async def get_job_queue(admin: bool = Depends(admin_only)) -> dict:
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")

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

    pending_jobs = [job for job in all_jobs if job["status"] == JobStatus.PENDING.value]
    processing_jobs = [
        job for job in all_jobs if job["status"] == JobStatus.PROCESSING.value
    ]
    completed_jobs = [
        job for job in all_jobs if job["status"] == JobStatus.COMPLETED.value
    ]
    failed_jobs = [job for job in all_jobs if job["status"] == JobStatus.FAILED.value]

    return {
        "total_jobs": len(all_jobs),
        "pending_jobs": pending_jobs,
        "processing_jobs": processing_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
