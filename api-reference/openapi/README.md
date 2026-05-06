# OpenAPI sources

Per-endpoint OpenAPI YAML files for the Vast.ai REST API.

## Files

- `yaml/` — one file per endpoint. Edit these.
- `build.py` — combines `yaml/*.yaml` into `../openapi.yaml` (the file Mintlify reads).

## Updating

```
npm run build-openapi   # rebuilds ../openapi.yaml
npm run check-openapi   # mint openapi-check
mint dev                # preview at http://localhost:3000
```

A pre-commit hook in `.githooks/pre-commit` will run the rebuild automatically when any source YAML is staged. Enable once per clone:

```
git config core.hooksPath .githooks
```

CI runs the same rebuild on every PR and fails if `openapi.yaml` is out of sync.

## Notes

- The build merges files that share an HTTP path. `instance_management.yaml` already combines start/stop/label/launch into one PUT path — the originals (`start_instance.yaml`, etc.) are listed in `YAML_IGNORE_LIST` in `build.py` to avoid double-merging.
- `openapi.yaml` is committed; it's the artifact Mintlify deploys.
