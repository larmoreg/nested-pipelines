from kfp import Client
from kfp.compiler import Compiler
from kfp.dsl import PipelineExecutionMode
from pydantic import BaseModel
import tempfile
from typing import Callable, Dict, Optional

from nested_pipelines.components import (
    combine_factory,
    download_factory,
    parse_factory,
)
from nested_pipelines.pipeline import Pipeline


def compile_pipeline(compiler: Compiler, pipeline: Callable) -> None:
    with tempfile.TemporaryDirectory() as temp:
        path = f"{temp}/pipeline.yaml"
        compiler.compile(pipeline, path)


def test_compile_download_artifact_pipeline(
    compiler: Compiler, download_artifact_pipeline: Callable
) -> None:
    compile_pipeline(compiler, download_artifact_pipeline)


def test_compile_download_parameter_pipeline(
    compiler: Compiler, download_parameter_pipeline: Callable
) -> None:
    compile_pipeline(compiler, download_parameter_pipeline)


def test_compile_parse_pipeline(compiler: Compiler, parse_pipeline: Callable) -> None:
    compile_pipeline(compiler, parse_pipeline)


def test_compile_combine_pipeline(compiler: Compiler, combine_pipeline: Callable) -> None:
    compile_pipeline(compiler, combine_pipeline)


def test_compile_parse_combine_pipeline(
    compiler: Compiler, parse_combine_pipeline: Callable
) -> None:
    compile_pipeline(compiler, parse_combine_pipeline)


def test_compile_combine_parse_pipeline(
    compiler: Compiler, combine_parse_pipeline: Callable
) -> None:
    compile_pipeline(compiler, combine_parse_pipeline)


def run_pipeline(client: Client, pipeline: Callable, url: str) -> None:
    client.create_run_from_pipeline_func(
        pipeline,
        arguments={"url": url},
        mode=PipelineExecutionMode.V2_COMPATIBLE,
    )


def test_run_download_artifact_pipeline(
    client: Client, download_artifact_pipeline: Callable, url: str
) -> None:
    run_pipeline(client, download_artifact_pipeline, url)


def test_run_download_parameter_pipeline(
    client: Client, download_parameter_pipeline: Callable, url: str
) -> None:
    run_pipeline(client, download_parameter_pipeline, url)


def test_run_parse_pipeline(client: Client, parse_pipeline: Callable, url: str) -> None:
    run_pipeline(client, parse_pipeline, url)


def test_run_combine_pipeline(client: Client, combine_pipeline: Callable, url: str) -> None:
    run_pipeline(client, combine_pipeline, url)


def test_run_parse_combine_pipeline(
    client: Client, parse_combine_pipeline: Callable, url: str
) -> None:
    run_pipeline(client, parse_combine_pipeline, url)


def test_run_combine_parse_pipeline(
    client: Client, combine_parse_pipeline: Callable, url: str
) -> None:
    run_pipeline(client, combine_parse_pipeline, url)


def test_nested_pipeline(url: str) -> None:
    def parse_combine_pipeline(spec: Dict) -> Dict:
        parse_task = parse_factory(
            parameters={
                "userId": "Integer",
                "id": "Integer",
                "title": "String",
                "completed": "Boolean",
            },
            name="parse-user",
        )(input=spec)
        combine_task = combine_factory(
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
        return combine_task.output

    def nested_pipeline(spec: Dict) -> Dict:
        parse_task = parse_factory(
            parameters={
                "url": "String",
            },
            name="parse-spec",
        )(input=spec)
        download_task = download_factory(parameters={"user": "typing.Dict"}, name="get-user")(
            user=parse_task.outputs["url"]
        )
        return parse_combine_pipeline(download_task.outputs["user"])

    class UserSpec(BaseModel):
        userId: int
        id: int
        title: str
        completed: bool

    class ParseCombinePipeline(Pipeline[UserSpec]):
        pipeline: Callable[[Dict], Optional[Dict]] = parse_combine_pipeline

    class NestedSpec(BaseModel):
        url: str

    class NestedPipeline(Pipeline[NestedSpec]):
        pipeline: Callable[[Dict], Optional[Dict]] = nested_pipeline

    bar = NestedPipeline()
    bar(NestedSpec(url=url))
