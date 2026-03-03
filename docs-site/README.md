# Maple Sim Docs (Fumadocs)

This directory contains the Fumadocs + Next.js site for Maple Sim documentation.

## Getting started

```bash
pnpm install
pnpm dev
```

The dev server runs at `http://localhost:3000`.

## Build / export

```bash
BASE_PATH=/maple-sim pnpm build
```

The Pages workflow uses `BASE_PATH=/maple-sim` to match GitHub Pages routing.

## Assets sync

Static assets from `/docs` (media, vendordep, javadocs) are copied into
`docs-site/public` before dev/build via:

```bash
pnpm predev
pnpm prebuild
```

## Updating docs content

Docs are sourced from `/docs` and converted to MDX under `docs-site/content`.
To re-run the conversion:

```bash
python3 scripts/convert_docs.py
```
