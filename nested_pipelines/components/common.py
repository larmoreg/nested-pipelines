from jinja2 import Environment, PackageLoader
from kfp.components import load_component_from_text
import os
from typing import Callable, Dict


def get_component_factory(
    filename: str,
) -> Callable:
    default_name = os.path.splitext(filename)[0]

    def component_factory(
        artifacts: Dict[str, str] = dict(),
        parameters: Dict[str, str] = dict(),
        name: str = default_name,
    ) -> Callable:
        assert artifacts or parameters, "Either artifacts or parameters is required."
        env = Environment(
            loader=PackageLoader("nested_pipelines.components", "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template(filename)
        return load_component_from_text(
            template.render(name=name, artifacts=artifacts, parameters=parameters)
        )

    return component_factory
