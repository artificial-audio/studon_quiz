# QTIConverter

Convert Markdown questions into ILIAS-compatible QTI packages.

## Installation Guide

To install and set up the QTIConverter project after downloading it from GitHub, follow these steps:

### Prerequisites
Ensure you have the following installed:
- Python 3.8 or higher
- [Poetry](https://python-poetry.org/) (for dependency management)

### Steps
1. **Clone the repository**:
    ```bash
    git clone https://github.com/artificial-audio/studon_quiz.git
    cd QTIConverter
    ```

2. **Install dependencies**:
    Use Poetry to install the project dependencies:
    ```bash
    poetry install
    ```

3. **Activate the virtual environment**:
    ```bash
    poetry shell
    ```

4. **Verify installation**:
    Run the following command to ensure the tool is installed correctly:
    ```bash
    qticonverter --help
    ```

You are now ready to use QTIConverter!

## Quick Start

### Generate templates
```bash
qticonverter generate-template --name demosa.md --folder templates/ --q_type mcq-sa
```
This command generates a template file named `demosa.md` in the `templates/` output folder for the `mcq-sa` question type.

#### Allowed question types:
- mcq-sa (Multiple Choice Question - Single Answer)
- mcq-ma (Multiple Choice Question - Multiple Answers)



### Convert all markdowns in the folder to QTI
To convert all Markdown files in a folder to a single QTI package, use the following command:

```bash
qticonverter convert-folder --input . --output demo_new.zip
```

This will process all Markdown files in the current directory and generate a QTI package named `demo_new.zip`.

### Convert a single question to QTI
To convert a single Markdown question file to a QTI package, use the following command:

```bash
qticonverter convert --input question.md --output question.zip
```

This will create a QTI package named `question.zip` from the specified `question.md` file.
