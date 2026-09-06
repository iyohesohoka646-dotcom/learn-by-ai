# Cross-session project discovery

Use this workflow whenever the learner names a subject or project without giving its state directory, including requests such as “start statistics learning,” “continue linear algebra,” or “resume my causal inference course.” Resolve project identity before initializing or teaching.

## Local registry

The portable registry is a local JSON file. Resolve it in this order:

1. an explicit registry path supplied by the learner or host;
2. `$LEARN_BY_AI_HOME/projects.json` when the environment variable is available;
3. `.learn-by-ai/projects.json` under the platform's user home directory;
4. an accessible workspace-local `.learn-by-ai/projects.json` when the host cannot read or write the user home directory.

Each entry records `project_id`, `name`, absolute `path`, `aliases`, `goal`, `tags`, `current_node`, project update time, and last verification time. The registry contains locators and brief routing metadata; keep learning evidence and source material inside the project directory.

When Python 3 is available, query it with one portable command:

```text
<python-3> <skill-dir>/scripts/project_registry.py find "<named subject>"
```

Add one or more explicitly authorized roots with `--scan-root <path>` when the registry has no useful match. Use `register <project-path>` to add or refresh an existing complete project. When Python is unavailable, read and update the same JSON structure with native file tools.

## Candidate resolution

Extract the named learning subject from the request, excluding action words such as start, learn, continue, or resume. Match candidates against project name, aliases, goal, and tags; use recency and current node only as supporting context.

Verify the six required sibling files before selecting a candidate. Handle results as follows:

- One clearly matching valid project: announce its name and absolute path, load its checkpoint, and continue.
- Several plausible projects: present a compact numbered choice showing name, path, goal, last update, and current node. Ask the learner to select one. Do not merge states, create another project, or begin teaching until the identity is resolved.
- Only stale or incomplete matches: report the path and missing files, then ask for a valid location or permission to repair the record.
- No match: run a bounded search only in the current workspace, its relevant parents, and learner-configured roots. If that still yields no match, offer to initialize a new project and state where it will be saved.

An explicit request to start a new project bypasses reuse after confirming the destination will not overwrite an existing state directory.

## Registration lifecycle

Register a project after successful initialization and refresh its entry whenever it is loaded from a new path or committed at a session boundary. Preserve aliases the learner uses for the project. If registry writing is unavailable, continue with the selected project and state that future cross-session discovery will require its path or an accessible registry.

Do not scan an entire disk or unrestricted home directory. Skip dependency, version-control, cache, build, and vendor directories. Search ends after the configured roots are checked or valid candidates are found.

## Host portability

Use optional host project or conversation search as an additional candidate source when available, while keeping the local registry authoritative for file-backed learning state. Render multiple choices with the host's native selector when one exists; otherwise use a numbered text list. The resolution rules stay the same across agents.
