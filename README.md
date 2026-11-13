# Eventhacker RFC

## Native image intake — issue 1

This initial development branch contains an offline intake check for original
PNG, JPEG and WebP files. It validates the actual format, dimensions, file
completeness and resource bounds. It returns the same bytes and their SHA-256
digest without resizing, re-encoding or producing an HTML wrapper.

Use the existing XvX environment; do not create another environment:

```sh
/home/magnetix/projects/xvx/xvx-venv/bin/python native_images.py original.png
/home/magnetix/projects/xvx/xvx-venv/bin/python -m unittest discover -s tests -v
```

The CLI emits metadata only. A successful local inspection explicitly reports
`uploaded: false`; it is not an AgentUp upload acknowledgment.

An image file can itself contain a screenshot, a border or interface elements.
Format validation cannot detect those reliably or recover the original asset.
The producing application must provide the original generated image file;
visual provenance remains a separate acceptance check.

## AgentUp integration is blocked on its authenticated API contract

The checked XvX Nextcloud configuration provides a private media-source link,
but no upload endpoint or authentication reference. No private link or secret
is copied into this repository. Do not reinterpret a browsing/share URL as an
authenticated upload API.

Before implementing the network adapter, provide through protected runtime
configuration:

- the authenticated upload endpoint and supported HTTP method/body format;
- a server-side credential reference and intended service identity;
- the successful response schema, including an asset identifier or URL;
- supported idempotency semantics and retryable failure responses;
- an authorized development endpoint for a real acknowledgment test.

The adapter must preserve the validated bytes, enforce TLS, bound timeouts and
retries, avoid logging response bodies or secrets, and distinguish confirmed
upload, failure and ambiguous outcomes. Automatic retries must depend on the
server's actual idempotency contract. Tests must cover those cases before any
upload can be reported as successful.

No native ChatGPT generation hook has been established. This repository does
not change ChatGPT's UI and cannot by itself make ChatGPT invoke an upload.
Only repository-side ingestion is currently prepared. No production deployment
or infrastructure change is authorized by issue 1.
