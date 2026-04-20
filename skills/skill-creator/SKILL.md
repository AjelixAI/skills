---
name: skill-creator
description: Create, edit, and optimize skills for Ajelix AI agents. Use when users want to create a new skill from scratch, modify or improve an existing skill, understand the skills format, or need guidance on skill structure, naming conventions, and best practices. Make sure to use this skill whenever the user mentions creating a skill, agent capabilities, or wants to package knowledge into a reusable format, even if they don't explicitly ask for a 'skill.'
version: "1.0.0"
---

# Skill Creator

A skill for creating new skills and iteratively improving them for Ajelix AI agents.

## Overview

Skills are how you give Ajelix AI agents new capabilities. A skill is simply a `SKILL.md` file inside a folder, with optional scripts, references, and assets.

**Location**: Skills live in `.ajelix/skills/` within an Ajelix project. When creating a new skill, always create a folder with the skill name and place the `SKILL.md` file inside it.

## Core Workflow

Creating a skill follows this loop:

1. **Capture Intent** — Understand what the skill should do
2. **Interview** — Ask about edge cases, formats, dependencies
3. **Write Draft** — Create the SKILL.md with proper frontmatter
4. **Review & Iterate** — Test with example prompts and refine

## Creating a Skill

### Step 1: Capture Intent

Understand the user's goal. Ask these questions:

1. **What should this skill enable the agent to do?**
   - Extract the target capability from the conversation or ask directly
2. **When should this skill trigger?**
   - What user phrases, keywords, or contexts should cause the agent to load this skill?
3. **What's the expected input/output format?**
   - File types, data formats, output structures
4. **Does it need test cases?**
   - Objective outputs (transforms, data extraction, code gen): yes
   - Subjective outputs (writing style, design): optional

### Step 2: Interview & Research

Ask about edge cases, dependencies, and example use cases. Check if existing skills cover similar ground — don't reinvent what already exists. Note these Ajelix-specific skills that are already available:

- `excel` — Spreadsheet work with formulas
- `docx` — Document creation/editing
- `pptx` — Presentation creation
- `pdf` — PDF manipulation
- `analyze-data` — Data analysis & statistics
- `web-search` — Internet search & research
- `web-assets-builder` — Visual outputs (HTML, charts, dashboards)

### Step 3: Write the SKILL.md

Create the file at `/mnt/.ajelix/skills/<skill-name>/SKILL.md`. Structure:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown body (instructions)
├── scripts/ (optional) — Executable Python/Bash scripts
├── references/ (optional) — Docs loaded into context on demand
└── assets/ (optional) — Templates, configs, images
```

### Frontmatter Rules

**name** (required):
- Max 64 characters
- Lowercase alphanumeric and hyphens only
- Must not start or end with hyphen (`-`)
- Must not contain consecutive hyphens (`--`)
- Must match the parent directory name

**description** (required):
- Max 1024 characters
- Must describe BOTH what it does AND when to trigger
- Include specific keywords so the agent reliably triggers the skill
- Make it somewhat "pushy" — list contexts where the skill should be used even if the user doesn't explicitly name it
- Be "pushy" about triggering — agents often undertrigger, so describe multiple ways the user might ask

**version** (recommended): Use semantic versioning, e.g., `"1.0.0"`

**allowed-tools** (optional): Space-separated list of tools the skill may use.

### Draft Template

Start every SKILL.md with this structure:

```yaml
---
name: my-skill
description: What it does and when to use it.
version: "1.0.0"
---

# Skill Title

Brief overview of what the skill does.

## Purpose
What problem this skill solves.

## Workflow
### Step 1: [Action]
Instructions, commands, or tool calls.

### Step 2: [Action]
...

### Step X: [Output]
Result format, file locations, user communication.
```

### Writing Guidelines

- **Use imperative form**: "Run the script", "Extract the text", not "The user should..."
- **Keep SKILL.md under 500 lines**: Move large reference content to `references/`
- **Reference files clearly**: Use relative paths from the skill root, e.g., `references/guide.md`
- **Explain the why**: Don't just say MUST — explain why so the agent understands the reasoning
- **Include examples**: Input/Output examples help the agent understand expected behavior
- **Avoid MUST/NEVER in all caps**: Use reasoning-based instructions instead of rigid constraints when possible
- **Progressive disclosure**: Keep the metadata small (~100 words), load references on demand

## Improving an Existing Skill

### Step 1: Assess the Current Skill
Read the existing SKILL.md and identify:
- Is the description clear and comprehensive?
- Are there unnecessary or redundant instructions?
- Does the skill handle common edge cases?
- Is the SKILL.md too long (over 500 lines) and should delegate to references?

### Step 2: Update the SKILL.md
Apply fixes based on the assessment. When updating:
- Preserve the original `name` field
- Update the `version` to reflect changes
- Keep changes incremental but impactful

### Step 3: Test with Real Prompts
Create 2-3 realistic test prompts — the kind of thing a real user would actually say. Run the agent through the prompts with access to the updated skill and verify outputs.

### Test Case Format

Save test prompts to track progress:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result"
    }
  ]
}
```

## Optimizing Skill Descriptions

The `description` field is the primary trigger mechanism. The agent reads only the `name` and `description` to decide whether to load a skill. To improve triggering:

1. **Think about all ways a user might ask**: Formal, casual, abbreviated, typo-prone
2. **Include related keywords**: If the skill handles PDFs, mention "document", "extract", "merge"
3. **List trigger contexts**: "Use when the user mentions X, Y, or Z"
4. **Handle near-misses**: Include contexts where the skill should trigger even though the user doesn't explicitly name the capability
5. **Add negative triggers if needed**: Consider cases where other skills might compete

### Example: Good vs Poor Description

**Poor**: `description: Helps with PDFs.`

**Good**: `description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, document extraction, or wants to combine or read any PDF file.`

## Ajelix-Specific Guidelines

When creating skills for Ajelix:

1. **File paths**: Always use absolute paths starting with `/mnt/` for user-visible files. Use `/mnt/.workspace/` for temporary/intermediate files.
2. **Output references**: When mentioning files in agent responses, always use markdown link format: `[filename](/mnt/path)`
3. **Tool access**: Specify which Ajelix tools the skill needs via `allowed-tools` or explicit instructions: `bash`, `read_file`, `write_file`, `skill`, `web_search`, `edit_file`, `write_file`, `glob`, `grep`, etc.
4. **Skills calling other skills**: If your skill needs another skill (e.g., your web search skill calls `web_search` tool), explicitly instruct the agent to `skill` tool load that skill first.
5. **Visual outputs**: For dashboards, charts, or HTML tools, instruct the agent to load `web-assets-builder` skill before creating HTML assets.
6. **Data work**: For spreadsheet analysis, instruct the agent to load `analyze-data` skill first.

## Package and Present

After finalizing the skill:
1. Verify the directory structure is correct
2. Check that `name` in frontmatter matches the directory name
3. Ensure all file references use correct relative paths
4. Validate that there are no syntax errors in the YAML frontmatter
5. Inform the user where the skill is located (it should be at `/mnt/.ajelix/skills/<skill-name>/SKILL.md`)
6. The skill will be automatically available to the agent on next use
