# Context and Entities

Understanding how context works is key to getting the most out of the SingleAgent system. This page explains what context is, how entities are tracked, and how context is shared between agents.

## What is Context?

Context is all the information the system keeps track of during your session. This includes:
- Files you add or reference
- Commands you run
- URLs and search queries
- Chat history with each agent
- Manually added notes or code snippets

Context helps the agents remember what you are working on, so you don't have to repeat yourself.

## Entities

Entities are specific items tracked by the system, such as:
- **Files**: Any file you add with `code:read:path` or reference in your conversation
- **Commands**: Shell or code commands you run or mention
- **URLs**: Web addresses you provide or that are found in your input
- **Search Queries**: Search terms you use
- **Design Patterns / Architecture Concepts**: (Architect Agent only) Patterns or concepts mentioned in your session

You can view all tracked entities with the `!entity` command. Entities are shared between agents, so switching agents does not lose your context.

## Manual Context Items

You can add files or notes to the context manually. These are called "manual context items" and can be listed with `!manualctx`. Each item has a label, source, and a token count (size).

To remove a manual context item, use `!delctx:label`.

## Persistent Context

Your context is saved automatically and restored when you restart the system. You can also save manually with `!save`.

---

For more on how agents use context, see `agents.md`.
