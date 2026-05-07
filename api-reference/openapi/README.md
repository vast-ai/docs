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

Commit the regenerated `../openapi.yaml` along with your YAML edits. CI re-runs the build on every PR and fails if `openapi.yaml` is out of sync — this is the safety net if you forget to rebuild.

## Notes

- The build merges files that share an HTTP path. `instance_management.yaml` already combines start/stop/label/launch into one PUT path — the originals (`start_instance.yaml`, etc.) are listed in `YAML_IGNORE_LIST` in `build.py` to avoid double-merging.
- `openapi.yaml` is committed; it's the artifact Mintlify deploys.
