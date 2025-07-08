# Anonymizer & De-anonymizer

A robust Python tool for anonymizing and de-anonymizing sensitive data in text files. This script uses Microsoft's Presidio library to detect and replace sensitive information with plausible fake data while maintaining the ability to restore the original data when needed.

## Introduction

The `anonymizer_deanonymizer.py` script provides a comprehensive solution for protecting sensitive information in text documents. It intelligently identifies sensitive data such as names, email addresses, Social Security Numbers (SSNs), and credit card numbers, then replaces them with realistic fake data. The anonymization process is fully reversible, allowing you to restore the original data when authorized.

## Features

- **Smart Detection**: Automatically detects various types of sensitive data including:
  - Personal names
  - Email addresses
  - Social Security Numbers (SSNs)
  - Credit card numbers
  - And more...

- **Reversible Anonymization**: Maintains a secure mapping between original and fake data for complete de-anonymization

- **Realistic Fake Data**: Generates plausible replacement data that maintains the structure and format of the original

- **File Organization**: Automatically creates timestamped directories for each anonymization session

- **Comprehensive Logging**: Detailed logging for tracking and debugging

- **Flexible Input**: Works with both file paths and direct text content

## Project Structure

```
anonymizer_deanonymizer/
├── anonymizer_deanonymizer.py    # Main script with AnonymizerDeAnonymizer class
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── test_anonymizer_deanonymizer.py  # Unit tests
└── test_answ_anonymizer.py       # Additional test file
```

### Key Files

- **`anonymizer_deanonymizer.py`**: The main script containing the `AnonymizerDeAnonymizer` class
- **`requirements.txt`**: Lists all required Python packages and their versions
- **`test_*.py`**: Test files to verify functionality

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Quick Installation (Recommended)

1. **Clone or download the repository**:
   ```bash
   git clone <repository-url>
   cd anonymizer_deanonymizer
   ```

2. **Install dependencies using requirements.txt**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install additional NLP models** (required for Presidio):
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Verify installation** by running the tests:
   ```bash
   python test_anonymizer_deanonymizer.py
   ```

### Manual Installation

If you prefer to install dependencies manually:

1. **Install core dependencies**:
   ```bash
   pip install presidio-analyzer
   pip install presidio-anonymizer
   ```

2. **Install additional NLP models**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Usage

### Basic Usage

Here's a simple example of how to use the anonymizer:

```python
from anonymizer_deanonymizer import AnonymizerDeAnonymizer
from pathlib import Path

# Initialize the anonymizer
anonymizer = AnonymizerDeAnonymizer()

# Sample text with sensitive data
text = """
Patient: John Smith
Email: john.smith@hospital.com
SSN: 123-45-6789
Medical notes: Patient shows signs of improvement.
"""

# Anonymize the text
output_dir = Path("./output")
anonymized_file, mapping_file = anonymizer.anonymize_text(
    text,
    output_dir,
    "patient_record"
)

print(f"Anonymized file created: {anonymized_file}")
print(f"Mapping file created: {mapping_file}")
```

### Anonymizing a File

```python
from anonymizer_deanonymizer import AnonymizerDeAnonymizer
from pathlib import Path

anonymizer = AnonymizerDeAnonymizer()

# Anonymize a file
input_file = Path("sensitive_document.txt")
output_directory = Path("./anonymized_output")

anonymized_file, mapping_file = anonymizer.anonymize_text(
    input_file,
    output_directory
)
```

### De-anonymizing Data

```python
# De-anonymize the previously anonymized file
deanonymized_file = anonymizer.deanonymize_text(
    anonymized_file,
    output_directory
)

print(f"Original data restored: {deanonymized_file}")
```

### Command Line Usage

You can also create a simple command-line interface:

```python
# cli_example.py
import sys
from pathlib import Path
from anonymizer_deanonymizer import AnonymizerDeAnonymizer

def main():
    if len(sys.argv) != 4:
        print("Usage: python cli_example.py <input_file> <output_dir> <action>")
        print("Actions: anonymize, deanonymize")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    action = sys.argv[3]
    
    anonymizer = AnonymizerDeAnonymizer()
    
    if action == "anonymize":
        anon_file, map_file = anonymizer.anonymize_text(input_file, output_dir)
        print(f"Anonymized: {anon_file}")
    elif action == "deanonymize":
        deanon_file = anonymizer.deanonymize_text(input_file, output_dir)
        print(f"De-anonymized: {deanon_file}")
    else:
        print("Invalid action. Use 'anonymize' or 'deanonymize'")

if __name__ == "__main__":
    main()
```

## Contributing

We welcome contributions to improve the Anonymizer & De-anonymizer tool! Here's how you can help:

### How to Contribute

1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** and ensure they follow the coding standards
4. **Write tests** for your new functionality
5. **Run existing tests** to ensure nothing is broken:
   ```bash
   python test_anonymizer_deanonymizer.py
   ```
6. **Commit your changes**: `git commit -m "Add your feature description"`
7. **Push to your branch**: `git push origin feature/your-feature-name`
8. **Create a Pull Request** on GitHub

### Development Guidelines

- Follow PEP 8 style guidelines
- Add comprehensive docstrings to all functions
- Include unit tests for new features
- Update documentation as needed
- Use meaningful commit messages

### Areas for Contribution

- Support for additional sensitive data types
- Performance optimizations
- Additional output formats
- Enhanced error handling
- Documentation improvements

## FAQs

### Q: What types of sensitive data can be detected?
**A:** The tool can detect names, email addresses, Social Security Numbers, credit card numbers, phone numbers, and other PII (Personally Identifiable Information) using Microsoft's Presidio library.

### Q: Is the anonymization process secure?
**A:** Yes, but remember that the mapping file contains the original sensitive data. Store mapping files securely and delete them when no longer needed.

### Q: Can I add custom data types for detection?
**A:** Yes! The script uses Presidio's pattern recognition system. You can extend the `__init__` method to add custom recognizers for specific data patterns.

### Q: What happens if the mapping file is lost?
**A:** Without the mapping file, de-anonymization is not possible. The anonymized data cannot be restored to its original form.

### Q: Does the tool work with non-English text?
**A:** Currently, the tool is configured for English text. However, Presidio supports multiple languages - you can modify the analyzer configuration to support other languages.

### Q: How do I handle large files?
**A:** The current implementation loads the entire file into memory. For very large files, consider processing them in chunks or using a streaming approach.

### Q: Can I customize the fake data generation?
**A:** Yes! You can modify the `_generate_fake_data` method to customize how fake data is generated for different entity types.

### Q: Is there a GUI version available?
**A:** Currently, this is a command-line tool. However, contributions for a GUI version are welcome!

## License

This project is licensed under the MIT License - see the LICENSE file for details.

```
MIT License

Copyright (c) 2025 Anonymizer & De-anonymizer Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

**Note**: This tool is designed for legitimate data protection purposes. Always ensure you have proper authorization before anonymizing or de-anonymizing any data, and comply with relevant privacy laws and regulations.
