# Changelog

All notable changes to the QTIConverter project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New question type `kprim` (ILIAS Kprim choice): exactly four statements, each judged true or false; optional front matter `points` and `partial_scoring` (three of four right give half points).

### Fixed
- LaTeX in list-format options and remarks was left as `{{QTILATEX_*}}` placeholders (#1).

## [0.2.0] - 2026-06-29

### Updates
- New question types added: essay and numerical. The README has been updated with detailed installation and usage instructions, including a section on reporting issues with guidelines for bug reports and feature requests.
- Program name changed from QTIConverter to studon_quiz to better reflect its purpose and functionality.
- Updated README with detailed installation and usage instructions
- Added reporting issues section with guidelines for bug reports and feature requests
- Better support for Markdown formatting, including handling of special characters and symbols



## [0.1.0] - 2026-03-09

### Initial Release

This is the first official release of QTIConverter, a tool for converting Markdown-formatted questions into ILIAS-compatible QTI packages.

### Features

#### Core Functionality
- **Markdown to QTI Conversion**: Convert Markdown-formatted quiz questions into QTI 1.2 packages compatible with ILIAS learning management system
- **Batch Processing**: Convert entire folders of Markdown files into a single QTI package
- **Single Question Conversion**: Convert individual Markdown question files to standalone QTI packages
- **Template Generation**: Generate Markdown templates for different question types to simplify question creation

#### Question Types
- **Multiple Choice - Single Answer (mcq-sa)**: Questions with multiple options where only one answer is correct
- **Multiple Choice - Multiple Answers (mcq-ma)**: Questions with multiple options where multiple answers can be correct

#### CLI Commands
- `qticonverter convert`: Convert a single Markdown question file to QTI package
- `qticonverter convert-folder`: Convert all Markdown files in a folder to a single QTI package
- `qticonverter generate-template`: Generate Markdown templates for different question types

#### Architecture
- Modular design with separate services for different conversion workflows
- Field-based question model for flexible question composition
- Comprehensive QTI XML generation with proper ILIAS compatibility
- Robust Markdown parsing using mistune library
- Question bank management for multi-question packages

### Technical Details

#### Dependencies
- Python 3.13+
- click 8.3.1+ (CLI framework)
- mistune 3.1.4+ (Markdown parsing)
- qti-package-maker 26.1rc4+ (QTI package generation)
- loguru 0.7.3+ (Logging)

#### Development Dependencies
- pytest 9.0.2+ (Testing framework)
- ipykernel 7.1.0+ (Jupyter notebook support)
- pylint 4.0.4+ (Code quality)

### Installation
- Poetry-based dependency management
- Installable as a command-line tool via `poetry install`
- Distributed under MIT License

### Testing
- Comprehensive test suite covering all major components
- Unit tests for questions, services, tools, CLI, and application layers
- Test coverage for Question, QuestionBank, QTI Writer, and conversion services

### Documentation
- README with installation guide
- Quick start guide with example commands
- Template examples for different question types

### Copyright
- Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
- Licensed under MIT License

---

## [Unreleased]

### Planned Features
- Additional question types (true/false, fill-in-the-blank, essay questions)
- Enhanced error handling and validation

---

## Version History

- **0.1.0** (2026-03-09): Initial release with core conversion features

[0.1.0]: https://github.com/artificial-audio/studon_quiz/tree/v0.1.0
