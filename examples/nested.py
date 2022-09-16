#!/usr/bin/env python3

from pydantic import BaseModel
from typing import Callable, Dict, Optional

from nested_pipelines.components import (
    combine_factory,
    download_factory,
    parse_factory,
)
from nested_pipelines.pipeline import Pipeline


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
    parse_task = parse_factory(parameters={"url": "String"}, name="parse-spec")(input=spec)
    download_task = download_factory(parameters={"user": "typing.Dict"})(
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


if __name__ == "__main__":
    pipeline = NestedPipeline()
    pipeline(NestedSpec(url="https://jsonplaceholder.typicode.com/todos/1"))
