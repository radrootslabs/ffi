# Radroots Python FFI library

Version 0.0.0 is unpublished. From the repository root, use `make test-python`
for local verification. Registry installation examples describe intended distributions.

Python FFI library for Radroots.

```bash
uv add radroots
```

```python
import radroots

assert radroots.name() == "Radroots"
radroots.print_name()
```
