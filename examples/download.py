#!/usr/bin/env python3

from kfp import Client
from kfp.dsl import PipelineExecutionMode
from kfp.v2.dsl import pipeline

from nested_pipelines.components import download_factory


@pipeline(name="download_pipeline")
def download_pipeline(url: str) -> None:
    download_factory(parameters={"user": "typing.Dict"})(user=url)


if __name__ == "__main__":
    client = Client()
    client.create_run_from_pipeline_func(
        download_pipeline,
        arguments={"url": "https://jsonplaceholder.typicode.com/todos/1"},
        mode=PipelineExecutionMode.V2_COMPATIBLE,
    )
