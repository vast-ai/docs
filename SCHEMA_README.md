# Schema.org Structured Data Implementation Guide

## Overview

This guide explains how to add Schema.org structured data to MDX files in the Vast.ai documentation to improve SEO and enable rich results in search engines.

## Files Already Implemented

The following files already have schema data implemented:
- ✅ `pytorch.mdx` - HowTo schema
- ✅ `documentation/get-started/index.mdx` - WebSite schema  
- ✅ `documentation/reference/faq/index.mdx` - FAQPage schema
- ✅ `docs.json` - Global schema in head section

## Implementation Pattern

Add the schema script **immediately after the frontmatter** and **before the main content**:

```jsx
---
title: Your Page Title
description: Your page description
---

<script type="application/ld+json" dangerouslySetInnerHTML={{
  __html: JSON.stringify({
    "@context": "https://schema.org",
    "@type": "YourSchemaType",
    // ... schema properties
  })
}} />

# Your Page Content Starts Here
```

## Common Schema Types for Documentation

### 1. Article/TechArticle
For tutorial and guide pages:
```jsx
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "Page Title",
  "description": "Page description",
  "author": {
    "@type": "Organization",
    "name": "Vast.ai Team"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Vast.ai",
    "logo": {
      "@type": "ImageObject",
      "url": "https://docs.vast.ai/logo/light.svg"
    }
  },
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD"
}
```

### 2. HowTo
For step-by-step guides:
```jsx
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "Guide Title",
  "description": "Guide description",
  "totalTime": "PT30M",
  "step": [
    {
      "@type": "HowToStep",
      "name": "Step Name",
      "text": "Step description"
    }
  ]
}
```

### 3. FAQPage
For FAQ sections:
```jsx
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Question text?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Answer text"
      }
    }
  ]
}
```

### 4. SoftwareApplication
For API documentation:
```jsx
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Vast.ai API",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Web"
}
```

## Research & Validation Requirements

Before implementing schema data, you **must**:

1. **Research appropriate schema types** at [Schema.org](https://schema.org)
2. **Test your implementation** using these tools:
   - [Google Rich Results Test](https://search.google.com/test/rich-results) - Test for Google compatibility
   - [Schema.org Validator](https://validator.schema.org/) - Validate schema syntax

## Implementation Steps

1. **Analyze content** - Determine the most appropriate schema type
2. **Research schema properties** - Check Schema.org documentation
3. **Implement schema** - Add the script block after frontmatter
4. **Validate** - Test with both validation tools
5. **Verify dates** - Use frontmatter `createdAt` and `updatedAt` for date fields

## Best Practices

- Use consistent author/publisher information (`Vast.ai Team`)
- Include relevant dates from frontmatter
- Keep descriptions concise but descriptive
- Use absolute URLs for images and links
- Test schema before committing changes
- Choose the most specific schema type available

## Validation Checklist

- [ ] Schema syntax is valid (Schema.org Validator)
- [ ] Rich results are detected (Google Rich Results Test)
- [ ] All required properties are included
- [ ] Dates match frontmatter values
- [ ] URLs are absolute and correct
- [ ] Content accurately reflects the page

## Need Help?

- [Schema.org Documentation](https://schema.org)
- [Google Structured Data Guidelines](https://developers.google.com/search/docs/appearance/structured-data)
- [Rich Results Test](https://search.google.com/test/rich-results)
- [Schema Validator](https://validator.schema.org/)
