# Living documentation

This site is generated from the repository, not maintained as a separate copy.
The root files remain the source of truth; the site is a projection of them.

## Source of truth

```mermaid
flowchart LR
    PLAN[plan.md] --> SITE[MkDocs site]
    INV[investigation.md] --> SITE
    FMT[format.md] --> SITE
    AG[AGENTS.md] --> SITE
    ST[handoff/script-status.md] --> SITE
    DIAG[docs/*.md<br/>UML · Mermaid] --> SITE
    SITE --> HTML[site/ · untracked]
```

The `include-markdown` plugin pulls the root files into the **Source documents**
section at build time. If a root document changes, the next build picks it up;
there is no second copy to update.

## Update loop

```mermaid
sequenceDiagram
    autonumber
    participant A as Analyst
    participant J as plan / investigation
    participant D as docs/
    participant M as MkDocs
    participant S as site/

    A->>J: append evidence or update state
    A->>D: update UML or page if the model changed
    A->>M: tools/docs.sh build
    M->>J: include current source
    M->>S: render HTML + Mermaid
    A->>S: inspect locally with tools/docs.sh serve
```

## Commands

```bash
# One-time environment
python3 -m venv .venv-docs
.venv-docs/bin/pip install -r requirements-docs.txt

# Live preview
tools/docs.sh serve

# Clean build
tools/docs.sh build
```

`tools/docs.sh` uses `.venv-docs` by default; override with
`DOCS_VENV=/path/to/venv`.

## Rules for a new page

1. Add `docs/<section>/<page>.md`.
2. Add a nav entry in `mkdocs.yml`.
3. Prefer a UML diagram over prose for structure.
4. Link to a source document instead of copying it.
5. Run `tools/docs.sh build` and check the Mermaid rendering.
6. Keep `site/` and `.venv-docs/` untracked.

## CI

`.github/workflows/docs.yml` builds the site on push and pull request and
uploads the rendered `site/` as an artifact. A Pages deployment can be added
later without changing the source layout.

!!! note "Living, not generated truth"
    The site does not replace `investigation.md` or `plan.md`. Evidence is
    appended there first; the site explains and visualizes it.
