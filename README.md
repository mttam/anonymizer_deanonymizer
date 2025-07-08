AnonymizerDeAnonymizer
A robust Python class for text anonymization and de-anonymization using the Presidio analyzer. This class identifies sensitive data in text, replaces it with plausible fake data, and provides a mechanism to revert the text to its original form.

Table of Contents
Features

Dependencies

How to Use

Initialization

Anonymizing Text

De-anonymizing Text

How It Works

Anonymization Process

De-anonymization Process

File Structure

Error Handling

Security Note

Features
PII Detection: Utilizes the presidio_analyzer to detect a wide range of personally identifiable information (PII), including names, email addresses, and US Social Security Numbers.

Custom Recognizers: Includes custom regex-based recognizers for improved detection of SSNs and email addresses.

Plausible Fake Data Generation: Replaces sensitive information with structurally similar fake data. For example, an email address is replaced by another valid-looking email address.

Stateless Design: The class is stateless and operates entirely through file I/O, making it predictable and easy to integrate into various workflows.

Reversible Process: Generates a mapping file that allows for the complete and accurate de-anonymization of the text.

Organized Output: Creates a unique, timestamped subdirectory for each anonymization task, keeping the output files organized.

Robust Logging: Implements comprehensive logging to track the process and assist in debugging.

Dependencies
The script requires the following Python libraries:

presidio_analyzer

pathlib

typing

logging

datetime

csv

You can install the primary dependency, Presidio, using pip:

pip install presidio-analyzer

How to Use
Initialization
First, create an instance of the AnonymizerDeAnonymizer class.

from your_module import AnonymizerDeAnonymizer

# Initialize the class
anonymizer = AnonymizerDeAnonymizer()

Anonymizing Text
You can anonymize text from either a string or a file path.

Example: Anonymizing a text string

# The text you want to anonymize
text_to_anonymize = "Contact John Doe at john.doe@example.com or call him. His SSN is 123-45-6789."

# Directory to store the output files
output_dir = "./output"

# Perform anonymization
anonymized_file_path, csv_map_path = anonymizer.anonymize_text(
    input_content=text_to_anonymize,
    output_base_directory=output_dir,
    original_file_name_for_output="contact_info"
)

print(f"Anonymized text saved to: {anonymized_file_path}")
print(f"Sensitive data map saved to: {csv_map_path}")

Example: Anonymizing a file

# Create a dummy file with sensitive data
with open("sensitive_document.txt", "w") as f:
    f.write("My name is Jane Smith and my email is jane.smith@workplace.com.")

# Directory to store the output files
output_dir = "./output"

# Perform anonymization
anonymized_file_path, csv_map_path = anonymizer.anonymize_text(
    input_content="sensitive_document.txt",
    output_base_directory=output_dir
)

print(f"Anonymized text saved to: {anonymized_file_path}")
print(f"Sensitive data map saved to: {csv_map_path}")

De-anonymizing Text
To restore the original text, you need the anonymized file and its corresponding output directory. The method will automatically find the correct mapping file based on the anonymized file's name.

# Path to the anonymized file from the previous step
# anonymized_file_path = Path('output/anonymization_20231027_103000_aBcDeFgHiJ/anonymized_contact_info_aBcDeFgHiJ.txt')

# The base directory where the anonymization output was stored
output_dir = "./output"

# Perform de-anonymization
deanonymized_file_path = anonymizer.deanonymize_text(
    anonymized_file_path=anonymized_file_path,
    output_base_directory=output_dir
)

print(f"De-anonymized text saved to: {deanonymized_file_path}")

# You can now read the restored content
with open(deanonymized_file_path, 'r') as f:
    original_text = f.read()
    print("\nRestored Text:")
    print(original_text)

How It Works
Anonymization Process
Unique ID Generation: A unique 10-character ID is generated for the anonymization session.

Output Directory Creation: A new subdirectory is created under the specified output_base_directory. The subdirectory is named using the current timestamp and the unique ID (e.g., anonymization_20231027_103000_aBcDeFgHiJ).

PII Analysis: The input text is analyzed by the Presidio AnalyzerEngine to identify sensitive entities.

Fake Data Generation: For each identified sensitive piece of data, a corresponding fake version is generated that preserves the data's structure.

Mapping File Creation: A CSV file (e.g., sensitive_data_contact_info_aBcDeFgHiJ.csv) is created inside the output subdirectory. This file maps each piece of original sensitive data to its generated fake counterpart.

Text Replacement: The original sensitive data in the text is replaced with the generated fake data.

Anonymized File Creation: The resulting anonymized text is saved to a .txt file (e.g., anonymized_contact_info_aBcDeFgHiJ.txt) in the output subdirectory.

De-anonymization Process
File Path Parsing: The method extracts the original base name and unique ID from the anonymized file's name.

Mapping File Location: It uses this information to locate the corresponding sensitive data CSV file within the same directory.

Mapping Data Loading: The CSV file is read into a dictionary, mapping the generated fake data back to the original sensitive data.

Text Restoration: The anonymized text is scanned, and each piece of fake data is replaced with its original version from the map.

De-anonymized File Creation: The fully restored text is saved to a new file (e.g., deanonymized_contact_info_aBcDeFgHiJ.txt).

Cleanup: The sensitive data mapping CSV file is automatically deleted for security.

File Structure
For each call to anonymize_text, a new directory is created with the following structure:

<output_base_directory>/
└── anonymization_<timestamp>_<unique_id>/
    ├── anonymized_<original_name>_<unique_id>.txt
    └── sensitive_data_<original_name>_<unique_id>.csv

After de-anonymization, the structure will be:

<output_base_directory>/
└── anonymization_<timestamp>_<unique_id>/
    ├── anonymized_<original_name>_<unique_id>.txt
    └── deanonymized_<original_name>_<unique_id>.txt

Error Handling
The class uses the logging module to provide detailed information about its operations.

Exceptions are logged with logger.error() before being re-raised. This ensures that failures are recorded without silently passing.

The script will raise exceptions for critical failures, such as being unable to create directories or find the necessary mapping file for de-anonymization.

Security Note
The sensitive data mapping CSV file is the key to reversing the anonymization. It contains the original, sensitive information.

Handle this file with extreme care.

Ensure that the output_base_directory is a secure location with restricted access.

The deanonymize_text method deletes the CSV file upon successful completion to minimize the risk of exposure. Do not disable this feature unless you have a specific, secure reason to do so.
