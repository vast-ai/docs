(function () {
  var ORG_SCHEMA_ID = "vast-organization-schema";
  var APP_SCHEMA_ID = "vast-application-schema";
  var PAGE_SCHEMA_ID = "vast-page-schema";
  var lastSignature = "";

  function addJsonLd(id, schema) {
    var existing = document.getElementById(id);
    if (existing) {
      existing.textContent = JSON.stringify(schema);
      return;
    }

    var script = document.createElement("script");
    script.id = id;
    script.type = "application/ld+json";
    script.textContent = JSON.stringify(schema);
    document.head.appendChild(script);
  }

  function canonicalUrl() {
    var canonical = document.querySelector('link[rel="canonical"]');
    return ((canonical && canonical.href) || window.location.origin + window.location.pathname).split("#")[0];
  }

  function metaContent(selector) {
    var meta = document.querySelector(selector);
    return meta ? meta.getAttribute("content") || "" : "";
  }

  function removeJsonLd(id) {
    var existing = document.getElementById(id);
    if (existing) {
      existing.remove();
    }
  }

  function pageTitle() {
    var title = document.title || "Vast.ai Documentation";
    return title.replace(/\s+-\s+Vast\.ai Documentation.*$/, "").trim() || "Vast.ai Documentation";
  }

  function pageDescription() {
    return (
      metaContent('meta[name="description"]') ||
      metaContent('meta[property="og:description"]') ||
      "Vast.ai documentation page for " + pageTitle() + "."
    );
  }

  function syncStructuredData() {
    var url = canonicalUrl();
    var title = pageTitle();
    var description = pageDescription();
    var signature = [window.location.pathname, url, title, description].join("|");

    if (signature === lastSignature) {
      return;
    }
    lastSignature = signature;

    addJsonLd(ORG_SCHEMA_ID, {
      "@context": "https://schema.org",
      "@type": "Organization",
      "name": "Vast.ai",
      "url": "https://vast.ai",
      "sameAs": [
        "https://twitter.com/vast_ai",
        "https://github.com/vast-ai",
        "https://www.youtube.com/@vast_ai/videos",
        "https://discord.gg/hSuEbSQ4X8"
      ]
    });

    addJsonLd(APP_SCHEMA_ID, {
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": "Vast.ai",
      "applicationCategory": "DeveloperApplication",
      "operatingSystem": "Web",
      "description": "Affordable GPU cloud marketplace for AI/ML workloads, 3D rendering, and high-performance computing.",
      "url": "https://vast.ai",
      "author": {
        "@type": "Organization",
        "name": "Vast.ai",
        "url": "https://vast.ai"
      },
      "offers": {
        "@type": "Offer",
        "category": "Cloud Computing",
        "description": "GPU cloud computing services"
      },
      "featureList": [
        "GPU Cloud Computing",
        "AI/ML Training",
        "3D Rendering",
        "Serverless Computing",
        "Virtual Machines",
        "Docker Containers"
      ]
    });

    if (window.location.pathname !== "/" && window.location.pathname !== "/guides/get-started") {
      addJsonLd(PAGE_SCHEMA_ID, {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": title,
        "description": description,
        "author": {
          "@type": "Organization",
          "name": "Vast.ai Team"
        },
        "publisher": {
          "@type": "Organization",
          "name": "Vast.ai",
          "url": "https://vast.ai",
          "logo": {
            "@type": "ImageObject",
            "url": "https://docs.vast.ai/logo/light.svg"
          }
        },
        "mainEntityOfPage": {
          "@type": "WebPage",
          "@id": url
        },
        "articleSection": "Documentation"
      });
    } else {
      removeJsonLd(PAGE_SCHEMA_ID);
    }
  }

  syncStructuredData();
  window.addEventListener("popstate", syncStructuredData);
  window.addEventListener("hashchange", syncStructuredData);
  window.setInterval(syncStructuredData, 1000);
})();
