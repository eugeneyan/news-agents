
```
q chat --trust-all-tools
Q, read context/main-agent.md and spin up sub agents to execute it.
```

## Main agent
- Reads `feeds.txt` to get feed URLs
- Divides feeds into 3 chunks of equal size
- Spawns 3 sub-agents, each assigned a chunk of feeds
- Monitors sub-agent progress and completion
- Aggregates all summaries into overall.md

## Sub agent
- Each sub-agent receives multiple feed URLs to process
- Processes feeds sequentially, completing one fully before starting the next
- For each feed:
  - Fetches feed content
  - Parses content
  - Summarizes stories
  - Saves summary to summaries/[feed-name].md immediately
- Reports "Feed processing complete" after finishing all assigned feeds

## Feedprocessing flow

```
Main Agent
├── Read feeds.txt
├── Divide into 3 chunks of [N] feeds each
├── Create 3 Sub-Agents
│   ├── Sub-Agent 1 (chunk 1)
│   │   ├── Feed #1: Fetch → Parse → Summarize → Save
│   │   ├── Feed #2: Fetch → Parse → Summarize → Save
│   │   ├── ...
│   │   ├── Feed #N: Fetch → Parse → Summarize → Save
│   │   └── Report "Feed processing complete"
│   ├── Sub-Agent 2 (chunk 2)
│   │   ├── Feed #1: Fetch → Parse → Summarize → Save
│   │   ├── Feed #2: Fetch → Parse → Summarize → Save
│   │   ├── ...
│   │   ├── Feed #N: Fetch → Parse → Summarize → Save
│   │   └── Report "Feed processing complete"
│   └── Sub-Agent 3 (chunk 3)
│       ├── Feed #1: Fetch → Parse → Summarize → Save
│       ├── Feed #2: Fetch → Parse → Summarize → Save
│       ├── ...
│       ├── Feed #N: Fetch → Parse → Summarize → Save
│       └── Report "Feed processing complete"
├── Collect all summaries from summaries/
└── Generate overall.md
```

## Debug with MCP inspector

```
uv run mcp dev src/main.p
```