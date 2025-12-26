# dbt-subprocess-plugin

This is a [dbt plugin][] to add Python's [`subprocess` module][subprocess] to dbt's [`modules` Jinja context][modules].

[dbt plugin]: https://github.com/dbt-labs/dbt-core/blob/fa96acb15f79ae4f10b1d78f311f5ef2f4ed645e/core/dbt/plugins/manager.py
[subprocess]: https://docs.python.org/3/library/subprocess.html
[modules]: https://docs.getdbt.com/reference/dbt-jinja-functions/modules

## Usage

1. Install `dbt-subprocess-plugin` into the same Python environment as dbt itself.
2. Start using it!

## Example

```console
$ dbt compile -q --inline '{{ modules.subprocess.check_output(["echo", "Hello from subprocess!"]) }}'
Hello from subprocess!
```
