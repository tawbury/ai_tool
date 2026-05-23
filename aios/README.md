# AIOS Shim Package

This package is a compatibility shim that lets the repository run `python -m aios` without installing the package.

The implementation lives in `src/aios/`.

## Files

| File | Purpose |
|---|---|
| `__init__.py` | Extends package lookup to `src/aios`. |
| `__main__.py` | Entrypoint for `python -m aios`. |
