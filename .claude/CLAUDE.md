# viral-ops — Claude Code Instructions

## Project overview

viral-ops is a Python CLI tool that scans YouTube channels, scores video virality, analyzes outliers with AI, and generates a dark-mode gallery + swipe file. It is a personal brand / marketing tool for its creator.

**Entry point:** `viral-ops` CLI → `viral_ops/__main__.py`  
**Data flow:** scanner → analyzer → gallery  
**Key files:** `viral_ops/scanner.py`, `viral_ops/analyzer.py`, `viral_ops/gallery.py`, `viral_ops/config.py`  
**Tests:** `pytest tests/` — 48 tests, must stay green  
**Repo:** `github.com/tabato/viral-ops`

## Core principles (Karpathy / anti-LLM-mistake guidelines)

### 1. Think before coding
- Surface assumptions before touching anything. If a request is ambiguous, name what's confusing and ask — don't guess and implement.
- If the right approach isn't clear, say so. One clarifying question is better than a wrong implementation.

### 2. Simplicity first
- Write the minimum code that solves the problem. Nothing speculative, nothing "while we're here."
- No premature abstractions. Three similar lines of code is better than a helper that might be needed someday.
- A bug fix doesn't need surrounding cleanup. A one-shot feature doesn't need a framework.

### 3. Surgical changes
- Edit only what the request requires. Every changed line should trace directly to what was asked.
- Don't refactor adjacent code. Don't rename things for style. Don't add error handling for scenarios that can't happen.
- If something nearby looks wrong but wasn't mentioned, flag it — don't silently fix it.

### 4. Goal-driven execution
- Before implementing anything non-trivial, define what "done" looks like. Run tests, check the output, verify the gallery renders.
- For UI changes (gallery.html), open it in the browser before declaring success.
- Tests must pass after every change. Run `PYTHONPATH=. pytest tests/ -q` to confirm.

## Project-specific conventions

- **Error messages** are written for non-technical users — plain English, specific fix instructions, no jargon
- **Gallery HTML** is generated as a single f-string in `gallery.py` — no template engine
- **AI providers** (Gemini, Claude, OpenAI) each have a dedicated setup doc (GEMINI.md, CLAUDE.md, OPENAI.md)
- **Sensitive files** (`.env`, `profile.yml`, `creators.yml`) are gitignored — never commit them
- **`scripts/`** is gitignored — personal/marketing tools, not public
- **`outliers.json`** is gitignored — generated output, not source

## What not to do

- Don't add features that weren't asked for
- Don't change the gallery CSS without running the tool and checking the browser output
- Don't commit `.env`, `profile.yml`, `creators.yml`, or anything in `scripts/`
- Don't break the 48-test suite — if a test fails after a change, fix it before moving on
