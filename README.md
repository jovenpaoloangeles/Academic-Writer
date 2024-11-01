# Academic Writer

A sophisticated academic writing assistant powered by LangGraph that automates the process of creating scholarly content through a coordinated system of AI agents.

## Overview

Academic Writer is an intelligent system designed to streamline the academic writing process. It employs a three-agent workflow:

1. **Planner Agent**: Structures and outlines the academic content
2. **Writer Agent**: Generates detailed academic text based on the plan
3. **Editor Agent**: Refines and polishes the written content

## Features

- Automated academic paper generation
- Structured writing workflow using LangGraph
- Multi-agent system for planning, writing, and editing
- Outputs in both DOCX and BIB formats
- Reference management and bibliography generation
- Iterative editing and refinement process

## System Architecture

The system uses a state-based graph workflow where:
- The planner creates an initial content structure
- The writer generates content iteratively
- The editor performs final refinements
- All agents coordinate through a shared state management system

## Output Formats

- **DOCX**: Final formatted academic paper
- **BIB**: Bibliography file with references

## Usage

```python
from academic_writer import process_writing_task

prompt = """Write a comprehensive review paper on [Your Topic]"""
result, docx_file, bib_file = process_writing_task(prompt)
```

## Requirements

See `requirements.txt` for a complete list of dependencies.

## Project Structure

```
├── academic_writer.py    # Main application file
├── modules/
│   ├── agents/          # AI agents
│   │   ├── planner.py   # Planning agent
│   │   ├── writer.py    # Writing agent
│   │   └── editor.py    # Editing agent
│   ├── state.py         # State management
│   ├── utils.py         # Utility functions
│   └── utils_doi.py     # DOI handling utilities
└── requirements.txt     # Project dependencies
