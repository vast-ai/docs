---
title: Zero Downtime Worker Update
description: Update your Serverless template or model without dropping in-flight requests.
"canonical": "/documentation/serverless/zero-downtime-worker-update"
---

<script type="application/ld+json" dangerouslySetInnerHTML={{
  __html: JSON.stringify({
    "@context": "https://schema.org",
    "@type": "TechArticle",
    "headline": "Zero Downtime Worker Update for Vast.ai Serverless",
    "description": "Learn how to update your Serverless template or model configuration without dropping in-flight requests. Vast orchestrates a graceful rolling update across your worker group automatically.",
    "author": {
      "@type": "Organization",
      "name": "Vast.ai"
    },
    "articleSection": "Serverless Documentation",
    "keywords": ["zero downtime", "rolling update", "worker", "template", "model", "serverless", "vast.ai", "graceful", "migration"]
  })
}} />

When you need to change the model or template behind a live Serverless endpoint, Vast can perform a **rolling update** that transitions every worker to the new configuration without dropping in-flight requests. From your users' perspective there is no downtime — existing requests complete normally, and new requests are routed to updated workers as they become available.

## When to Use This

A zero downtime update is useful any time you need to change the backend of a live endpoint, for example:

- Upgrading to a newer version of your template.
- Switching to a different model (e.g., moving from `Qwen/Qwen3-8B` to `Qwen/Qwen3-14B`).
- Adjusting vLLM launch arguments or other environment variables in the template.
- Adding or changing the search filter on your worker group.

## How to Trigger an Update

The process requires two steps:

### 1. Update your template

Modify the template that your endpoint uses. This could involve changing the `MODEL_NAME`, updating `VLLM_ARGS`, or selecting an entirely new template version.

### 2. Update the worker group configuration

Once the template is saved, update your worker group to reference the new template. This signals Vast to begin the rolling update.

<Note>
  After you complete these two steps, Vast handles the rest automatically. No additional action is required on your part.
</Note>

## What Happens During the Update

Vast orchestrates the transition across your worker group in the following sequence:

1. **Inactive workers become active and update** — Any inactive workers are brought into an active state, updated to the new template and model configuration, and made available for requests.
2. **Active workers finish existing tasks first** — Workers that are currently active and handling requests are allowed to complete all of their in-flight tasks before updating. Once an active worker finishes its current work, it updates to the new configuration and rejoins the pool.
3. **New requests route to updated workers** — As updated workers come online, incoming requests are directed to them. This continues until every worker in the group is running the new configuration.

Because active workers are never interrupted mid-request, no responses are dropped or truncated during the rollout.

## Best Practices

- **Schedule updates during low-traffic periods** — While the update process is designed to be seamless, performing it during a period of stable, low traffic reduces the number of in-flight requests that need to drain and shortens the overall transition window.
- **Verify the new template independently** — Before triggering a rolling update on a production endpoint, consider testing the new template on a separate endpoint to confirm that the model loads correctly and produces the expected output.
- **Monitor during the rollout** — Keep an eye on your endpoint's request latency and error rate while the update is in progress. A brief increase in latency is normal as the worker pool transitions, but errors may indicate a problem with the new configuration.
