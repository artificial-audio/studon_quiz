# studon_quiz

Convert Markdown questions into ILIAS-compatible QTI packages.

## Installation Guide

To install and set up the studon_quiz project after downloading it from GitHub, follow these steps:

### Prerequisites
Ensure you have the following installed:
- Python 3.8 or higher
- [Poetry](https://python-poetry.org/) (for dependency management)

### Steps
1. **Clone the repository**:
    ```bash
    git clone git@github.com:artificial-audio/studon_quiz.git
    cd studon_quiz
    ```

2. **Install dependencies**:
    Use Poetry to install the project dependencies:
    ```bash
    poetry install
    ```

3. **Verify installation**:
    Run the following command to ensure the tool is installed correctly:
    ```bash
    poetry run studon_quiz --help
    ```

You are now ready to use studon_quiz!

## Quick Start

### Generate templates
```bash
poetry run studon_quiz generate-template --name demosa.md --folder templates/ --q_type mcq-sa
```
This command generates a template file named `demosa.md` in the `templates/` output folder for the `mcq-sa` question type.

#### Allowed question types:
- mcq-sa (Multiple Choice Question - Single Answer)
- mcq-ma (Multiple Choice Question - Multiple Answers)
- essay (Essay Question)
- num (Numerical Question)

Edit the files using Obsidian (Preferred) or any Markdown editor, then convert them to QTI packages using the commands below.

### Convert all markdowns in the folder to QTI
To convert all Markdown files in a folder to a single QTI package, use the following command:

```bash
poetry run studon_quiz convert-folder --input . --output demo_new.zip
```

This will process all Markdown files in the current directory and generate a QTI package named `demo_new.zip`.

### Convert a single question to QTI
To convert a single Markdown question file to a QTI package, use the following command:

```bash
poetry run studon_quiz convert-single --input question.md --output question.zip
```

This will create a QTI package named `question.zip` from the specified `question.md` file.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
