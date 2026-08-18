# Knowledge graph and learner overlay

Use a sparse, goal-aligned graph. Do not attempt to model an entire discipline during initialization.

## Contents

- [Static node schema](#static-node-schema)
- [Edge schema](#edge-schema)
- [Learner-state overlay](#learner-state-overlay)
- [Route construction](#route-construction)

## Static node schema

Every active node should contain:

```yaml
id: probability.random-variable.distribution
name: Distribution of a random variable
aliases: [probability distribution]
type: concept
summary: A minimal original summary, not copied source text.
scope:
  includes: [distribution function, induced measure]
  excludes: [parameter estimation]
learning_objectives:
  - Distinguish a random variable, its distribution, a density, and point probability.
prerequisites: [probability.random-variable]
relations:
  - type: contrasts-with
    target: probability.density
source_refs:
  - resource: primary-text
    locator: chapter 3, section 2
    role: primary
assessment_refs: [diagnostic.distribution.01]
common_misconceptions: [density value equals probability]
applications: [simulation, statistical modeling]
target_depth: derivation-and-application
goal_weight: high
estimated_minutes: 90
provenance: resource-index
confidence: medium
version: "0.1"
```

Required semantics:

- `id` is stable, unique, lowercase, and domain-prefixed.
- `summary` is the smallest useful model of the idea; it does not replace the source.
- `scope` prevents neighboring topics from silently merging.
- `learning_objectives` are observable tasks, not phrases such as “understand X.”
- `source_refs` use resource IDs plus locators. Never embed substantial source text.
- `provenance` and `confidence` distinguish verified structure from model inference.
- `target_depth`, `goal_weight`, and `estimated_minutes` are relative to the project.

## Edge schema

Support `prerequisite-of`, `part-of`, `generalizes`, `specializes`, `derived-from`, `contrasts-with`, `commonly-confused-with`, `used-by`, `applies-to`, `transfers-to`, and `assessed-by`.

Record important edges as objects with `source_refs`, `provenance`, and `confidence`. Put uncertain edges in `candidate_edges` until evidence or a source confirms them. Reject cycles among strict prerequisite edges unless the modeling error can be split into smaller nodes.

## Learner-state overlay

Keep user state separate from static nodes:

```yaml
node_id: probability.random-variable.distribution
learning_status: learning
mastery:
  conceptual: 1
  derivation: 0
  standard_problem: 1
  transfer: 0
  application: 0
  oral_expression: 0
  retention: 0
evidence_strength: low
attempt_refs: [attempt-20260817-001]
error_profile:
  object-confusion:
    count: 1
    last_seen: "2026-08-17T10:00:00Z"
hint_dependency:
  highest_recent_level: 1
  recent_count: 1
self_confidence: 3
last_seen: "2026-08-17T10:00:00Z"
last_assessed: "2026-08-17T10:00:00Z"
review_due: null
blocked_by: []
recommended_action: minimal-example-and-transfer-check
```

Use mastery levels `0` through `4`:

- `0`: untested or insufficient evidence;
- `1`: recognize and explain basic meaning in own words;
- `2`: independently complete a standard task;
- `3`: solve a near transfer and explain conditions/boundaries;
- `4`: prove, construct a counterexample, model, or transfer across contexts.

Do not average dimensions into a single score. A learner may calculate well while lacking conceptual, transfer, application, expression, or retention evidence.

## Route construction

1. Extract candidate nodes from the goal and resource tables of contents.
2. Merge aliases while preserving source-specific terminology.
3. Add only the prerequisite chain, current goal nodes, near comparisons, and immediate applications.
4. Assign goal weight and target depth.
5. Mark inferred nodes/edges with low or medium confidence.
6. Ask the learner to review high-impact uncertain structure when practical.
7. Expand the graph when a new blocker, transfer target, or resource requires it.
