import subprocess
from functools import wraps

import dbt.context.base
from dbt.plugins.manager import dbtPlugin


class DbtSubprocessContextPlugin(dbtPlugin):
    """Adds Python's subprocess module to dbt's `modules` context."""

    def initialize(self) -> None:
        self._get_context_modules_orig = dbt.context.base.get_context_modules

        @wraps(self._get_context_modules_orig)
        def _wrapper():
            return {
                **self._get_context_modules_orig(),
                "subprocess": get_subprocess_module_context(),
            }

        dbt.context.base.get_context_modules = _wrapper
    


def get_subprocess_module_context():
    context_exports = subprocess.__all__
    return {name: getattr(subprocess, name) for name in context_exports}


plugins = [DbtSubprocessContextPlugin]
