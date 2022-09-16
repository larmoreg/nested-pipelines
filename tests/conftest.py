from kfp import Client
from kfp.compiler import Compiler
from kfp.dsl import get_pipeline_conf, PipelineExecutionMode
import kfp.onprem as onprem
from kfp.v2.dsl import pipeline
import pytest
from typing import Callable

from nested_pipelines.components import (
    combine_factory,
    download_factory,
    parse_factory,
)


@pytest.fixture(scope="session")
def client() -> Client:
    return Client()


@pytest.fixture(scope="session")
def compiler() -> Compiler:
    return Compiler(mode=PipelineExecutionMode.V2_COMPATIBLE)


@pytest.fixture(scope="session")
def url() -> str:
    return "https://jsonplaceholder.typicode.com/todos/1"


@pytest.fixture(scope="session")
def download_artifact_pipeline() -> Callable:
    @pipeline(name="test")
    def test(url: str) -> None:
        download_factory(parameters={"user": "Artifact"})(user=url)

    test.__name__ = "download_artifact_pipeline"
    return test


@pytest.fixture(scope="session")
def download_parameter_pipeline() -> Callable:
    @pipeline(name="test")
    def test(url: str) -> None:
        download_factory(parameters={"user": "typing.Dict"})(user=url)

    test.__name__ = "download_parameter_pipeline"
    return test


@pytest.fixture(scope="session")
def parse_pipeline() -> Callable:
    @pipeline(name="test")
    def test(url: str) -> None:
        download_task = download_factory(parameters={"user": "typing.Dict"})(user=url)
        parse_factory(
            parameters={
                "userId": "Integer",
                "id": "Integer",
                "title": "String",
                "completed": "Boolean",
            }
        )(input=download_task.outputs["user"])

    test.__name__ = "parse_pipeline"
    return test


@pytest.fixture(scope="session")
def combine_pipeline() -> Callable:
    @pipeline(name="test")
    def test(url: str) -> None:
        get_pipeline_conf().add_op_transformer(
            onprem.use_k8s_secret(
                secret_name="mlpipeline-minio-artifact",
                k8s_secret_key_to_env={
                    "accesskey": "AWS_ACCESS_KEY_ID",
                    "secretkey": "AWS_SECRET_ACCESS_KEY",
                },
            )
        )
        download_task = download_factory(artifacts={"user": "Artifact"})(user=url)
        combine_factory(artifacts={"user": "Artifact"}, parameters={"url": "String"})(
            user=download_task.outputs["user"], url=url
        )

    test.__name__ = "combine_pipeline"
    return test


@pytest.fixture(scope="session")
def parse_combine_pipeline() -> Callable:
    @pipeline(name="test")
    def test(url: str) -> None:
        download_task = download_factory(parameters={"user": "typing.Dict"})(user=url)
        parse_task = parse_factory(
            parameters={
                "userId": "Integer",
                "id": "Integer",
                "title": "String",
                "completed": "Boolean",
            }
        )(input=download_task.outputs["user"])
        combine_factory(
            parameters={
                "userId": "Integer",
                "id": "Integer",
                "title": "String",
                "completed": "Boolean",
            }
        )(
            userid=parse_task.outputs["userId"],
            id=parse_task.outputs["id"],
            title=parse_task.outputs["title"],
            completed=parse_task.outputs["completed"],
        )

    test.__name__ = "parse_combine_pipeline"
    return test


@pytest.fixture(scope="session")
def combine_parse_pipeline() -> Callable:
    @pipeline(name="test")
    def test(url: str) -> None:
        get_pipeline_conf().add_op_transformer(
            onprem.use_k8s_secret(
                secret_name="mlpipeline-minio-artifact",
                k8s_secret_key_to_env={
                    "accesskey": "AWS_ACCESS_KEY_ID",
                    "secretkey": "AWS_SECRET_ACCESS_KEY",
                },
            )
        )
        download_task = download_factory(artifacts={"user": "Artifact"})(user=url)
        combine_task = combine_factory(
            artifacts={"user": "Artifact"}, parameters={"url": "String"}
        )(user=download_task.outputs["user"], url=url)
        parse_factory(artifacts={"user": "Artifact"}, parameters={"url": "String"})(
            input=combine_task.output
        )

    test.__name__ = "combine_parse_pipeline"
    return test
