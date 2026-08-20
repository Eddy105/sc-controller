## Tests

The test suite uses [pytest](https://docs.pytest.org/).

From the repository root:

```bash
python -m pytest tests
```

The same command is used by GitHub Actions CI. Some tests exercise Linux- and
GTK-specific behavior and may require additional system dependencies on a
local development machine.
