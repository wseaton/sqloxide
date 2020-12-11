from typing import Any, Dict

from setuptools_rust import RustExtension


def build(setup_kwargs: Dict[str, Any]) -> None:
    setup_kwargs.update(
        {
            "rust_extensions": [RustExtension("sqloxide.sqloxide", "Cargo.toml", debug=False)],
            "zip_safe": False
        }
    )