from abc import ABC, abstractmethod
from datetime import timedelta
from kfp import Client
from kfp.compiler import Compiler
from kfp.dsl import get_pipeline_conf, PipelineExecutionMode
from kfp.onprem import use_k8s_secret
from kfp.v2.dsl import pipeline
from typing import Any, Callable, cast, Dict, Generic, Optional

from .types import PipelineStatus, T


class Pipeline(ABC, Generic[T]):
    @property
    @staticmethod
    @abstractmethod
    def pipeline() -> Callable[[Dict], Optional[Dict]]:
        ...

    def _get_pipeline(self) -> Callable[[Dict], Optional[Dict]]:
        @pipeline(name=self.__class__.pipeline.__name__)
        def _pipeline(input: Dict) -> None:
            get_pipeline_conf().add_op_transformer(
                use_k8s_secret(
                    secret_name="mlpipeline-minio-artifact",
                    k8s_secret_key_to_env={
                        "accesskey": "AWS_ACCESS_KEY_ID",
                        "secretkey": "AWS_SECRET_ACCESS_KEY",
                    },
                )
            )
            self._output = cast(Callable[[Dict], Optional[Dict]], self.__class__.pipeline)(input)

        _pipeline.__name__ = self.__class__.pipeline.__name__
        return _pipeline

    def __init__(self) -> None:
        self.client = Client()
        self.compiler = Compiler(mode=PipelineExecutionMode.V2_COMPATIBLE)

    def compile(self, package_path: str = "pipeline.yaml") -> None:
        self.compiler.compile(self.__class__.pipeline, package_path)

    def __call__(self, input: T, **kwargs: Any) -> PipelineStatus:
        request = self.client.create_run_from_pipeline_func(
            self._get_pipeline(),
            arguments=dict(input=input.dict(exclude_none=True)),
            mode=PipelineExecutionMode.V2_COMPATIBLE,
            **kwargs,
        )
        return PipelineStatus(id=request.run_info.id, status=request.run_info.status)

    def update(self, status: PipelineStatus) -> PipelineStatus:
        return PipelineStatus(id=status.id, status=self.client.get_run(status.id).run.status)

    def wait(self, status: PipelineStatus, timeout: Optional[int] = None) -> PipelineStatus:
        if status.complete:
            return status

        response = self.client.wait_for_run_completion(
            status.id,
            timedelta(seconds=timeout) if timeout is not None else timedelta.max,
        )
        return PipelineStatus(id=response.run.id, status=response.run.status)

    def run(self, input: T, timeout: Optional[int] = None, **kwargs: Any) -> PipelineStatus:
        status = self(input, **kwargs)
        status = self.wait(status, timeout=timeout)
        return status
