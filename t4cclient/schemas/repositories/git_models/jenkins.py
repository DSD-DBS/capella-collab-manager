import typing as t

from pydantic import BaseModel


class CreateJenkinsJob(BaseModel):
    name: str

    class Config:
        orm_mode = True


class JenkinsRun(BaseModel):
    id: int
    result: str
    start_time: str
    logs_url: str

    class Config:
        orm_mode = True


class JenkinsPipeline(CreateJenkinsJob):
    id: int
    latest_run: t.Optional[JenkinsRun]
