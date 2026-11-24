# GraftFork Rules

- Never force-move or push a `graft/<release>` branch when tests fail on either the upstream baseline or the moved tree.
- Always preserve the original commit message / rationale when rewriting a conflicting patch hunk.
- Prefer read-only dry carry reports before mutating remote branches.
