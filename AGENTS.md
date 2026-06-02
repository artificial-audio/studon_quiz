## Agent Instructions


### Context

To ensure reliable and context-aware operation, always populate the directory structure relevant to the file or task at hand:

- Use the available directory listing tool to retrieve the folder structure up to a depth of **at least 3** from the file of interest.
- This should be done at the start of a session or before performing actions that depend on file relationships or locations.
- Keeping this context up to date helps the agent understand file locations, dependencies, and relationships without repeated tool calls.


---
### Behavior Guidelines
- **Delegate to sub-agents** If a task falls within the scope of a subagent always use it. 
- **Always make use of the tools and skills at your disposal.**
- **Make use of lsp server for code understanding and generation tasks.**
- **Actively suggest concrete options and next steps** rather than asking excessive clarifying questions.
- **When uncertainty exists**, propose a reasonable default or most common path forward.

---
### Temp Folder Usage
- When converting quizzes or using any qticonverter tools, always perform these actions inside the `temp` folder.
- All files for testing and experimentation should be created and managed within the `temp` directory to keep the workspace organized and isolated from production files.


### Workflow Principles
These points capture the non-obvious, repo-specific workflow needed for reliable use of **QTIConverter**.
