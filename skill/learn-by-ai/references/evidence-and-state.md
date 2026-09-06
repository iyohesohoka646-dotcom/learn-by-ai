# Evidence, state updates, review, and checkpoints

Raw evidence and summarized state are separate. The log explains why the current state exists; the overlay makes continuation efficient.

## Evidence event schema

Append one JSON object per important attempt or correction:

```json
{
  "event_id": "attempt-20260817-001",
  "event_type": "attempt",
  "timestamp": "2026-08-17T10:00:00Z",
  "node_id": "probability.random-variable.distribution",
  "task": {"type": "near-transfer", "source_ref": "primary-text#ch3-s2-ex4"},
  "answer_summary": "Distinguished the variable from its CDF but treated density value as probability.",
  "result": "partial",
  "hints": {"highest_level": 1, "count": 1},
  "earliest_breakpoint": "object-confusion",
  "error_category": "density-as-probability",
  "conditions_explained": false,
  "transfer_completed": false,
  "dimensions": ["conceptual", "transfer"],
  "supersedes": null
}
```

Use `result` values `correct`, `partial`, `incorrect`, or `not-assessed`. Summarize the answer structure and decisive evidence; do not retain irrelevant chat. Never store model impressions as evidence.

Keep the log append-only. To correct an event, append a new `event_type: correction` event whose `supersedes` points to the old event.

## Evidence-to-level rules

- Own-words recognition/recall can support conceptual level `1` only.
- Independent standard performance can support `standard_problem: 2`.
- Near transfer plus condition explanation can support `transfer: 3` and relevant conceptual/derivation dimensions.
- Proof, counterexample construction, modeling, or cross-context transfer can support the relevant dimension at `4`.
- Success after a meaningful interval strengthens `retention` and `evidence_strength`.
- Strongly hinted work is partial evidence; do not count it as independent performance.
- “I understand” updates `self_confidence`, not mastery.

One success should rarely stabilize an important node. Seek either a different task type or later retrieval. A recent failure does not erase all earlier success; classify whether it reveals a condition gap, task-specific error, transfer gap, or forgetting.

## State fields and status transitions

Use statuses `unseen`, `diagnosing`, `learning`, `fragile`, `stable`, `review-due`, and `blocked`.

Keep mastery dimensions separate: `conceptual`, `derivation`, `standard_problem`, `transfer`, `application`, `oral_expression`, and `retention`.

Use `fragile` when some target evidence exists but is narrow, hinted, contradictory, or unretained. Use `stable` only when target dimensions have adequate independent evidence. Use `blocked` only with explicit `blocked_by` node IDs. Use `review-due` when a stable/fragile node reaches its scheduled check.

## Review policy

1. When a node becomes stable, set `last_assessed` and a reasonable `review_due` date/condition.
2. At review, use retrieval or transfer before explanation.
3. On success, extend the interval and strengthen retention evidence.
4. On failure, distinguish forgetting, condition confusion, and transfer failure.
5. Reteach fully only when evidence shows the conceptual structure is lost.
6. Prioritize review by due status, goal weight, and whether it blocks the active route.

The MVP does not require a complex scheduler.

## Commit transaction

At a session boundary:

1. Append evidence events and verify each line is valid JSON.
2. Update referenced `attempt_refs`, mastery dimensions, evidence strength, error profile, hint dependency, dates, blockers, and recommended action in `learner-state.yaml`.
3. Update static graph or resource metadata only if newly learned information changes them.
4. Update project routing fields and timestamps.
5. Write `checkpoint.md` last so it never claims a state update that failed.
6. Refresh the cross-session registry entry after the project transaction succeeds. Preserve the project commit if registry refresh fails and report the discoverability gap.

## Checkpoint contract

The checkpoint must be short enough to load first and complete enough to resume without chat history. Include:

- project goal and graph version;
- session end time and stop reason;
- current node and learning status;
- completed nodes with achieved depth;
- sources used and exact locators;
- the active lesson contract and whether its completion condition was met;
- external research gaps, unresolved source conflicts, and deferred topics that could affect continuation;
- new mastery evidence and its strength;
- misconceptions, errors, and earliest breakpoint;
- incomplete work and blockers;
- reviews due;
- next node and intended course package;
- graph/resource-index changes;
- exactly one discriminating opening question.
