from abc import ABC, abstractmethod
from typing import Any

from app.models.job import Job
from app.services.agent_orchestrator import AgentOrchestrator



class JobDispatcher(ABC):
    """
    Abstract base class for job execution dispatchers.
    Decouples HTTP request lifecycles from background task execution backends (Sync, Celery, Redis Queue, etc.).
    """

    @abstractmethod
    def dispatch(self, job: Job) -> None:
        """Dispatch a Job to be processed by the AI orchestration pipeline."""
        ...


class SyncJobDispatcher(JobDispatcher):
    """
    Synchronous job dispatcher implementation.
    Executes the AgentOrchestrator synchronously on the current thread.
    """

    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator

    def dispatch(self, job: Job) -> None:
        self.orchestrator.run(job)


class BackgroundTaskJobDispatcher(JobDispatcher):
    """
    Asynchronous job dispatcher implementation using FastAPI BackgroundTasks.
    """

    def __init__(self, orchestrator: AgentOrchestrator, background_tasks: Any):
        self.orchestrator = orchestrator
        self.background_tasks = background_tasks

    def dispatch(self, job: Job) -> None:
        self.background_tasks.add_task(self.orchestrator.run, job)

