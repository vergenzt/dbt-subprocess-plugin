import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import tinypg
from pytest import fixture

DBT_PROFILES_DIR = Path(__file__).parent
DBT_PROFILE = "test_profile"
DBT_PROJECT_NAME = "test_" + re.sub(
    r"[^\w]", "_", os.getenv("ENV_NAME", DBT_PROFILES_DIR.parent.name).lower()
)
DBT_PROJECT_YML: str = json.dumps(
    {
        "name": DBT_PROJECT_NAME,
        "version": "0.0.1",
        "profile": DBT_PROFILE,
        "model-paths": ["models"],
        "target-path": "target",
    }
)


@fixture(autouse=True)
def dbt_project(tmp_path, monkeypatch):
    dbt_project_path = tmp_path / DBT_PROJECT_NAME
    dbt_project_path.mkdir()
    dbt_project_path.joinpath("dbt_project.yml").write_text(DBT_PROJECT_YML)
    dbt_project_path.joinpath("models").mkdir()
    dbt_project_path.joinpath("target").mkdir()

    monkeypatch.setenv("DBT_PROFILES_DIR", str(DBT_PROFILES_DIR))
    monkeypatch.setenv("DBT_PROJECT_DIR", str(dbt_project_path))

    with tinypg.database() as dburl_str:
        dburl = urlparse(dburl_str)
        monkeypatch.setenv("DB_HOST", dburl.hostname or "")
        monkeypatch.setenv("DB_USERNAME", dburl.username or "")
        monkeypatch.setenv("DB_PASSWORD", dburl.password or "")
        monkeypatch.setenv("DB_PORT", str(dburl.port))
        monkeypatch.setenv("DB_NAME", dburl.path[1:] or "")
        monkeypatch.setenv("DB_SCHEMA", "public")
        monkeypatch.chdir(dbt_project_path)

        yield dbt_project_path


def test_plugin_works(dbt_project: Path):
    model_path = dbt_project / "models" / "test.sql"
    model_path.write_text("""
    select '{{ modules.subprocess.check_output(["bash", "-c", "echo foo"], text=True).strip() }}'
    """)

    from dbt.cli.main import cli

    cli(["compile"], standalone_mode=False)

    model_compiled_path = (
        dbt_project / "target/compiled" / model_path.relative_to(dbt_project.parent)
    )
    assert model_compiled_path.read_text().strip() == "select 'foo'"
