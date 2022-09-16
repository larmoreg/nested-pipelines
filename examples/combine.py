#!/usr/bin/env python3

from kfp import Client
from kfp.dsl import PipelineExecutionMode
from kfp.v2.dsl import pipeline

from nested_pipelines.components import (
    combine_factory,
    download_factory,
    parse_factory,
)


@pipeline(name="parse_combine_pipeline")
def parse_combine_pipeline(url: str) -> None:
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


if __name__ == "__main__":
    client = Client()
    client.create_run_from_pipeline_func(
        parse_combine_pipeline,
        arguments={"url": "https://jsonplaceholder.typicode.com/todos/1"},
        mode=PipelineExecutionMode.V2_COMPATIBLE,
    )
