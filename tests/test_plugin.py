import os
import re
from pathlib import Path
from subprocess import check_call

from pytest import fixture

DBT_PROFILES_DIR = Path(__file__).parent
DBT_PROFILE = "test_profile"
DBT_PROJECT_NAME = "test_" + re.sub(r"[^\w]", "_", os.getenv("ENV_NAME", "dbt_subprocess").lower())


@fixture(autouse=True)
def dbt_project(tmp_path, monkeypatch):
    monkeypatch.setenv("DBT_PROFILES_DIR", str(DBT_PROFILES_DIR))
    check_call(["dbt", "init", f"--profile={DBT_PROFILE}", DBT_PROJECT_NAME], cwd=tmp_path)
    monkeypatch.setenv("DBT_PROJECT_DIR", str(dbt_project_path := tmp_path / DBT_PROJECT_NAME))
    monkeypatch.setenv("DB_PATH", str(tmp_path / DBT_PROJECT_NAME / "target" / "db"))
    return dbt_project_path


def test_plugin_works(dbt_project: Path):
    model_path = dbt_project / "models" / "test.sql"
    model_path.write_text("""
    select '{{ modules.subprocess.check_output(["bash", "-c", "echo foo"], text=True).strip() }}'
    """)

    check_call(["dbt", "compile"])

    model_compiled_path = (
        dbt_project / "target/compiled" / model_path.relative_to(dbt_project.parent)
    )
    assert model_compiled_path.read_text().strip() == "select 'foo'"
