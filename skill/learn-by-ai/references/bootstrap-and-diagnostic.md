# Bootstrap and diagnostic

Use this workflow after creating project files or when rebuilding an unreliable initial state.

## Scriptless initialization

Use this only when Python 3 is unavailable. Create the destination directory, copy the six files from `assets/learning-project-template/`, and replace every `{{UPPERCASE_MARKER}}` with a correctly escaped value. Use JSON double-quoted strings for YAML scalar markers; JSON strings are valid YAML scalars.

Replace `PROJECT_ID`, `PROJECT_NAME`, `PROJECT_GOAL`, `PROJECT_ALIASES`, `PROJECT_TAGS`, `TARGET_DEPTH`, `SESSION_MINUTES`, and `CREATED_AT` in the YAML/Markdown files. Use JSON arrays for aliases and tags. Replace the `_JSON` markers with valid JSON strings and create a unique `EVENT_ID_JSON` plus an ISO-8601 UTC `TIMESTAMP_JSON` in `evidence.jsonl`. Verify that no `{{...}}` marker remains and that every non-empty `evidence.jsonl` line is valid JSON.

Refuse to overwrite any of the six state files. If a write fails after creating some files, remove only the files created by this attempt or report the partial state precisely; never delete pre-existing user files.

After successful initialization, register the verified absolute project path as described in [project-discovery.md](project-discovery.md). If the registry is inaccessible, report the path and continue; the six project files remain authoritative.

## 1. Collect minimum context

Gather:

- final goal and time horizon;
- desired depth: overview, exam, research, engineering, or comprehensive;
- available textbooks, problem sets, notes, exams, code, and other materials;
- relevant prior background and self-assessment;
- normal session length and any hard constraints.

The observable goal is mandatory. If target depth is omitted and does not immediately change the first diagnostic, use `comprehensive` provisionally and record that default. Time horizon and prior background may remain `unknown`; do not invent them. Ask only for missing facts that materially change the route. Self-assessment guides sampling but is not mastery evidence.

## 2. Index resources

For each material, record:

```yaml
- id: stable-resource-id
  title: Human-readable title
  kind: textbook
  role: primary
  path_or_url: ./materials/example.pdf
  version: unknown
  language: en
  accessibility: accessible
  searchable: true
  coverage: [candidate topics]
  preferred_for: [definitions, course spine]
  teaching_authority: true
  locator_precision: section
  limitations: []
  last_checked: "2026-08-17"
```

Valid roles include `primary`, `rigorous-deepening`, `problem-bank`, `exam`, `application`, `code`, and `notes`.

Use `teaching_authority: true` for the accessible source that should govern sequence, notation, definitions, and standard methods. Use `locator_precision` values such as `page`, `section`, or `topic` to prevent false precision. Normally only one source has teaching authority for a node; other sources retain their specialist roles.

When a resource is mentioned but not provided or cannot be opened, keep a minimal entry in `resources` so its intended role is not lost, and add a matching failure record:

```yaml
unavailable_resources:
  - resource_id: mentioned-primary-text
    reason: not-provided
    blocks: [source-aligned-definitions, exact-section-locators]
    checked_at: "2026-08-17"
    next_action: ask-for-file-or-use-labeled-substitute
```

Use `reason` values such as `not-provided`, `cannot-open`, `image-only`, or `not-searchable`. An unavailable source does not block a goal-based diagnostic; it blocks only steps whose fidelity depends on that source.

For each file:

1. Verify identity/version when possible.
2. Verify that it can actually be opened and searched.
3. Read the table of contents, index, headings, and only representative sections needed for alignment.
4. Assign a role based on demonstrated coverage, not title alone.
5. Mark inaccessible or image-only material explicitly; do not claim it was checked.
6. Store locators and original summaries, not book chapters or long passages.

Do not build OCR, a vector database, or a full-text mirror as part of this skill.

## 3. Create the candidate graph

1. Extract goal-relevant nodes from the goal and source structures.
2. Merge synonyms, translations, and notation variants.
3. Connect prerequisites, components, contrasts, applications, and assessments.
4. Set target depth, goal weight, source references, provenance, and confidence.
5. Keep unverified relations in `candidate_edges`.
6. Limit the initial graph to the main route and nearby dependencies.

Follow [graph-model.md](graph-model.md) for schemas.

## 4. Run a compact adaptive diagnostic

Sample anchor nodes rather than exhaustively testing the graph. The diagnostic should usually fit 15–30 minutes of active work and cover several evidence types.

For each anchor:

1. Start with a medium-difficulty discriminating task.
2. If correct, probe upward with explanation, changed conditions, derivation, or application.
3. If incorrect, probe downward toward object, definition, and prerequisites.
4. Stop probing once the entry level and first breakpoint are sufficiently identified.
5. Record hints and uncertainty.

Across the diagnostic include a compact mix of conceptual explanation, standard procedure, derivation/proof skeleton, condition or counterexample reasoning, near transfer, and oral-style explanation/application/code when relevant.

Never infer failure for untested nodes. Keep them at level `0` with low/unknown evidence.

## 5. Produce the initial route

After the diagnostic, write:

- demonstrated capability anchors;
- critical breakpoints;
- high-risk prerequisites;
- uncertain/untested nodes;
- the main route entry;
- the first course package;
- one opening question that distinguishes the next branch.

Append diagnostic attempts to `evidence.jsonl`, summarize them in `learner-state.yaml`, set `current_node` in `project.yaml`, and write `checkpoint.md` last.
