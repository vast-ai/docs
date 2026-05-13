# Vast.ai Documentation

Source for [docs.vast.ai](https://docs.vast.ai), the official documentation for the Vast.ai GPU cloud marketplace. Covers renting or hosting GPU instances, deploying serverless inference workloads, and using the CLI, SDK, and REST API.

## Updating the API reference

API endpoint specs live in `api-reference/openapi/yaml/` (one file per endpoint). The combined spec consumed by Mintlify is `api-reference/openapi.yaml`.

1. Edit the relevant file in `api-reference/openapi/yaml/`.
2. Rebuild the combined spec: `npm run build-openapi`.
3. Validate: `npm run check-openapi`.
4. Preview locally: `mint dev`.
5. Commit both your YAML edit AND the regenerated `api-reference/openapi.yaml`, then open a PR. CI re-runs the build and fails if `openapi.yaml` is out of sync with the sources.

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
