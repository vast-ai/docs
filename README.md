# Vast.ai Documentation

Source for [docs.vast.ai](https://docs.vast.ai), the official documentation for the Vast.ai GPU cloud marketplace. Covers renting or hosting GPU instances, deploying serverless inference workloads, and using the CLI, SDK, and REST API.

## Updating the API reference

API endpoint specs live in `api-reference/openapi/yaml/` (one file per endpoint). The combined spec consumed by Mintlify is `api-reference/openapi.yaml`.

1. Edit the relevant file in `api-reference/openapi/yaml/`.
2. Rebuild the combined spec: `npm run build-openapi`.
3. Validate: `npm run check-openapi`.
4. Preview locally: `mint dev`.
5. Commit both your YAML edit AND the regenerated `api-reference/openapi.yaml`, then open a PR. CI re-runs the build and fails if `openapi.yaml` is out of sync with the sources.

## Updating the self-test reference

The host self-test reference page is generated from the Vast CLI diagnostics and the self-test image metadata.

1. Update the relevant self-test source in `vast-ai/vast-cli` or `vast-ai/self-test`.
2. Regenerate the docs page:

```bash
npm run generate-self-test-reference -- --vast-cli ../vast-cli --self-test ../self-test
```

3. Review and commit `host/self-test-reference.mdx` with the source change or in the matching docs PR.
4. CI re-runs the generator against `vast-ai/vast-cli` and `vast-ai/self-test` and fails if the committed page is out of sync.

For cross-repo private checkouts, configure the docs repository secret `VAST_DOCS_SOURCE_TOKEN` with read access to `vast-ai/vast-cli` and `vast-ai/self-test`. The workflow can also be run manually with custom `vast_cli_ref` and `self_test_ref` inputs while a source PR is under review.

Source repositories can trigger the docs check after self-test metadata changes by sending a repository dispatch event to `vast-ai/docs`:

```json
{
  "event_type": "self-test-reference-source-updated",
  "client_payload": {
    "vast_cli_ref": "master",
    "self_test_ref": "main"
  }
}
```

Use the exact branch or SHA being validated when triggering this from a source PR workflow.

## Mintlify Information

**[Follow the full quickstart guide](https://starter.mintlify.com/quickstart)**

Install the [Mintlify CLI](https://www.npmjs.com/package/mint) to preview your documentation changes locally. To install, use the following command:

```
npm i -g mint
```

Run the following command at the root of your documentation, where your `docs.json` is located:

```
mint dev
```

View your local preview at `http://localhost:3000`

## Publishing changes

Install our GitHub app from your [dashboard](https://dashboard.mintlify.com/settings/organization/github-app) to propagate changes from your repo to your deployment. Changes are deployed to production automatically after pushing to the default branch.

## Need help?

### Troubleshooting

- If your dev environment isn't running: Run `mint update` to ensure you have the most recent version of the CLI.
- If a page loads as a 404: Make sure you are running in a folder with a valid `docs.json`.

### Resources
- [Mintlify documentation](https://mintlify.com/docs)
- [Mintlify community](https://mintlify.com/community)
