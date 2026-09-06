---
name: learn-by-ai
description: Run long-term, evidence-based adaptive learning and reconnect named study requests to local project records across sessions. Use when a learner says to start, continue, or resume learning a subject; for systematic study plans, source-grounded teaching, layered practice, review, or maintaining a knowledge graph and learner record. Keep isolated questions outside the full protocol unless the learner requests tracking.
---

# Learn by AI

Use explicit project files as durable learning state. Treat the model's conversational memory as convenient context, never as the source of truth.

## Resolve the learning project first

When the learner says “start,” “continue,” “resume,” or “learn” a named subject without a path, search for its existing local project before choosing a mode or teaching. Read [project-discovery.md](references/project-discovery.md) and use this precedence:

1. an explicit project path from the learner;
2. the local Learn by AI project registry;
3. a bounded search in the current workspace, relevant parents, and configured project roots;
4. optional host project or conversation search when available.

Verify all six state files before loading a candidate. If one project clearly matches, announce its absolute path and continue from its checkpoint. If several projects plausibly match, show a numbered choice with each name, path, goal, last update, and current node; wait for the learner to select one. Never combine parallel states or silently initialize a duplicate. If no valid match exists, offer to initialize a new project and state its proposed location.

Use the bundled registry helper when Python 3 is available:

```text
<python-3> <skill-dir>/scripts/project_registry.py find "<named subject>"
```

The registry defaults to `$LEARN_BY_AI_HOME/projects.json` or `.learn-by-ai/projects.json` under the platform user home. If that location is inaccessible, use an explicit accessible registry path or a workspace-local fallback. Python is optional; agents may read and update the JSON registry with native file tools.

## Decide the operating mode

Choose exactly one mode before teaching:

1. **Initialize** — discovery found no valid project and the learner confirms a new systematic program, or the learner explicitly requests a new project.
2. **Continue** — a complete project exists and the user wants to resume, review, or be tested.
3. **One-off** — answer normally without creating state when the request is isolated and the user did not ask to track it.

If the request is ambiguous, state the lightweight one-off assumption and offer to add the result to a project after answering. Never silently create a long-term record.

## Locate or initialize the project

A complete project contains these sibling files:

```text
project.yaml
resource-index.yaml
knowledge-graph.yaml
learner-state.yaml
evidence.jsonl
checkpoint.md
```

Project identity must already be resolved through the preceding discovery workflow. Do not combine states from different directories.

For a new project, the observable learning goal is mandatory. Ask for missing target depth only when it materially changes the route; otherwise use `comprehensive` provisionally and label it as a default. Unknown time horizon, background, and unprovided materials may remain unknown rather than blocking initialization. Default to a 120-minute course package when session length is not specified.

If a Python 3 launcher is available, run the bundled non-destructive initializer. Replace `<python-3>` with the platform's Python 3 command, such as `python3`, `python`, or `py -3`:

```text
<python-3> <skill-dir>/scripts/init_learning_project.py <destination> --name "<project name>" --goal "<observable learning goal>" --depth <overview|exam|research|engineering|comprehensive> --session-minutes <minutes>
```

Do not require Python or a particular shell. When the platform cannot run the initializer, follow the scriptless initialization procedure in [bootstrap-and-diagnostic.md](references/bootstrap-and-diagnostic.md) using the agent's native file tools.

The initializer refuses to overwrite any existing state file and registers a successful project for cross-session discovery. If it reports a conflict, inspect the directory and ask whether to use a different destination; do not delete or replace files automatically. If registry writing fails, preserve the initialized project and tell the learner its absolute path.

After initialization, read [bootstrap-and-diagnostic.md](references/bootstrap-and-diagnostic.md), index the available resources, create only the local graph needed for the current route, and run a compact adaptive diagnostic.

## Load state before acting

In **Continue** mode, read in this order:

1. `project.yaml` for goal, constraints, active node, and graph version.
2. `checkpoint.md` for the last natural stopping point and unique opening question.
3. `learner-state.yaml` for mastery dimensions, blockers, due reviews, and uncertainty.
4. `resource-index.yaml` for source roles and accessibility.
5. Relevant nodes and edges from `knowledge-graph.yaml`; avoid unrelated branches.
6. Only evidence events referenced by active nodes when detailed justification is needed.

Orient the learner in four short items before continuing: current node, unresolved issue, today's target, and materials to be used. Do not re-diagnose stable facts unless evidence is stale or contradictory.

## Follow the control loop

Use this state machine for every formal session:

```text
Load -> Orient -> Frame -> Search corpus -> Research -> Freeze plan -> Teach -> Assess
                                                                         ^          |
                                                                         |          +-> Advance
                                                                         |          +-> Refine
                                                                         |          +-> Remediate
                                                                         |          +-> Review
                                                                         +----------+
Assess/Teach -> Stop -> Commit
```

At each transition:

1. **Frame** — choose the next node and define the observable outcome, scope, likely prerequisites, and a provisional boundary.
2. **Search corpus** — search the indexed master documents first and extract only the relevant definitions, arguments, examples, and locators.
3. **Research** — search authoritative papers, official material, or strong explanatory sources for current evidence, rigor, intuition, or applications that the corpus does not supply.
4. **Freeze plan** — turn the source pack into a flexible lesson contract with a completion condition, budget, and detour rule.
5. **Teach** — teach the concept before expecting independent performance: anchor the explanation to the source pack, then move through a complete explanation, guided derivation, and independent transfer.
6. **Assess** — obtain observable evidence through explanation, calculation, derivation, variation, application, code, or oral defense.
7. **Advance** only when evidence supports the target dimension.
8. **Refine** the earliest failed reasoning step; do not merely lengthen the explanation.
9. **Remediate** the shortest missing prerequisite chain when the current node is blocked.
10. **Review** with retrieval or transfer before deciding to reteach.

Read [retrieval-and-planning.md](references/retrieval-and-planning.md) before preparing a new teaching unit or substantial reteach. Read [control-policy.md](references/control-policy.md) for node selection, source routing, teaching moves, error actions, and stopping rules. Read [graph-model.md](references/graph-model.md) whenever creating or revising graph structure.

## Prepare a bounded teaching unit

Before teaching a new node, search the project's indexed master documents for the relevant section, then run targeted external research when search tools are available. Build a small source pack that covers the planned claims, conditions, example, and assessment; preserve verified locators and label any unresolved conflict or access gap. Do not repeat research on every conversational turn or keep searching after additional sources have little chance of changing the lesson.

Convert that source pack into a flexible lesson contract: observable outcome, prerequisite assumptions, included and deferred scope, conceptual arc, teaching and assessment moves, approximate budget, completion evidence, and detour rule. Adapt the contract when learner evidence changes the route, while keeping one active objective and one active prerequisite detour. End or checkpoint at the completion condition, the time boundary, or a natural split; place useful discoveries outside the current scope in a backlog.

## Teach from the learner's materials

When a primary textbook, course note, paper, or other teaching source is available, let it determine the concept order, notation, theorem framing, and standard method. Use other sources for rigor, counterexamples, applications, or practice according to their indexed roles; do not replace the primary source with a model-generated course without saying so.

Before a formal teaching segment, report the selected source, verified chapter/section or topic locator, the content being taught, and any supplement with its purpose. Never guess a page, section, theorem, or exercise number. Label model-created explanations, examples, and tasks as `teacher-created` or `teacher-integrated`; do not present them as source content.

Default each new concept to a three-phase teaching cycle:

1. **Complete teaching** — motivation, object and definition, mechanism or derivation, one worked example, and one contrast or failure case.
2. **Guided derivation** — provide the structure and let the learner complete the decisive step.
3. **Independent transfer** — use a coherent medium-to-hard task that changes conditions or context and requires independent method choice.

Do not substitute a stream of exercises for teaching. Keep each learner prompt coherent rather than splitting it into many tiny questions; split only at the confirmed earliest breakpoint. Report the node, evidence, uncertainty, breakpoint, and cycle progress after the cycle or at a natural stop, while still recording important attempts as they occur.

## Apply the core rules

### Invocation

- Activate the full protocol for systematic study, material-based planning, adaptive questioning, review, cross-session continuation, or explicit progress tracking.
- Keep a one-off answer outside the project unless the user requests recording.
- Report inaccessible or unsearchable material honestly. It blocks only actions that require that material, not a goal-based initial diagnostic. Use an accessible substitute only after labeling the substitution.
- Store summaries and locators, not copyrighted book text or entire chapters.

### Assessment

- Never convert “I understand” into mastery by itself.
- Mark untested dimensions as `0`/unknown evidence, not as failure.
- Treat one correct answer as limited evidence; important nodes need evidence across task types or time.
- Discount evidence completed with strong hints and record the hint level.

### Refinement

- Find the first breakpoint: object, symbol/shape, definition/quantifier, prerequisite, mechanism, theorem condition, method choice, derivation, computation, transfer, expression, or retention.
- Change one thing at a time: smaller task, minimal example, contrast case, missing step, or nearest prerequisite.
- After the same breakpoint fails twice, stop adding new material, shrink the task one level, retest, and if still blocked create or activate a prerequisite node.

### Stopping

- A question awaiting the learner's answer is a **turn wait**, not a session stop.
- A natural boundary or prerequisite detour is a **node pause**, not necessarily the end of the session.
- End the **session** when the prepared package is complete, effective learning reaches the time limit at a natural boundary, the user asks to stop/summarize/switch, the request is explicitly one-off, required material is unavailable, or the remaining work must become a separate prerequisite unit.
- After deciding to end, introduce no new knowledge. Summarize and commit state only.

## Build a two-hour course package

Unless the project overrides it, prepare approximately:

- 10 minutes: retrieval and prediction;
- 25 minutes: motivation, objects, and definitions;
- 25 minutes: mechanism, derivation, or proof skeleton;
- 35 minutes: worked example and layered practice;
- 15 minutes: application, simulation, or code;
- 10 minutes: oral explanation, recall, and state commit.

This is content capacity, not a single response. Pause for learner answers throughout; waiting time does not consume effective learning time.

For a different session length, multiply each block by `session_minutes / 120`, round to practical five-minute blocks, and preserve the same order. Keep at least five minutes for recall and commit; shorten examples before removing the final assessment/commit block.

## Record evidence and commit

Read [evidence-and-state.md](references/evidence-and-state.md) before grading important work or updating state.

For each important attempt, append one JSON object to `evidence.jsonl` containing the node, task type/source, answer summary, result, hint level/count, earliest breakpoint, error category, transfer/condition evidence, affected mastery dimensions, and timestamp. Keep raw evidence append-only; corrections are new events that reference the superseded event.

At a session boundary, commit in this order:

1. Append all new evidence events.
2. Update `learner-state.yaml` from those events, preserving uncertainty and conflicting evidence.
3. Update `knowledge-graph.yaml`, `resource-index.yaml`, or `project.yaml` only when structure, sources, goal, or route changed.
4. Replace `checkpoint.md` last, after all other writes succeed.
5. Refresh the local registry entry with the verified path, aliases, update time, and current node; a registry failure must not invalidate the project commit.

The checkpoint must state completed nodes and depth, sources used, new evidence, misconceptions and first breakpoint, unfinished work, due reviews, blockers, next node, graph/index changes, and exactly one opening question for the next session.

Finish by telling the learner what was recorded, what remains uncertain, the next node, and the next-session opening question.

## Reference routing

- Cross-session project lookup, disambiguation, and registry lifecycle: [project-discovery.md](references/project-discovery.md)
- Initialization, materials, diagnostic: [bootstrap-and-diagnostic.md](references/bootstrap-and-diagnostic.md)
- Master-document retrieval, external research, and flexible lesson planning: [retrieval-and-planning.md](references/retrieval-and-planning.md)
- Node/edge schema and route construction: [graph-model.md](references/graph-model.md)
- Invocation, planning, teaching, refinement, stopping: [control-policy.md](references/control-policy.md)
- Evidence schema, mastery updates, review, checkpoint: [evidence-and-state.md](references/evidence-and-state.md)
