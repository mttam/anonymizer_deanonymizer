import logging
from typing import Union, Tuple, Optional, Dict
from pathlib import Path
import random
import string
import csv
from datetime import datetime
import shutil
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider

class AnonymizerDeAnonymizer:
    """
    A class that provides robust methods for text anonymization and de-anonymization.
    This class is stateless and relies on file I/O for all operations.
    """ 
    def __init__(self):
        """Initialize the AnonymizerDeAnonymizer with logging configuration."""
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize the Presidio analyzer with custom configuration
        try:
            self.analyzer = AnalyzerEngine()
            
            # Add custom regex patterns for better SSN detection
            ssn_pattern = Pattern(
                name="ssn_pattern",
                regex=r"\b\d{3}-\d{2}-\d{4}\b",
                score=1.0
            )
            ssn_recognizer = PatternRecognizer(
                supported_entity="US_SSN",
                patterns=[ssn_pattern]
            )
            
            # Add custom regex pattern for better email detection
            email_pattern = Pattern(
                name="email_pattern",
                regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                score=1.0
            )
            email_recognizer = PatternRecognizer(
                supported_entity="EMAIL_ADDRESS",
                patterns=[email_pattern]
            )
            
            # Add both recognizers
            self.analyzer.registry.add_recognizer(ssn_recognizer)
            self.analyzer.registry.add_recognizer(email_recognizer)
            self.logger.info("Successfully initialized Presidio analyzer with custom patterns")
        except Exception as e:
            self.logger.error(f"Failed to initialize Presidio analyzer: {str(e)}")
            raise

    def _generate_unique_id(self) -> str:
        """
        Generate a random 10-character alphanumeric ID.
        
        Returns:
            str: A unique 10-character alphanumeric ID.
        """
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=10))

    def _create_output_subdirectory(self, base_dir: Union[str, Path], unique_id: str) -> Path:
        """
        Create a new subdirectory within the base directory for output files.
        
        Args:
            base_dir: The base directory where the subdirectory will be created.
            unique_id: The unique ID to be used in the subdirectory name.
            
        Returns:
            Path: The path to the created subdirectory.
        """
        base_dir_path = Path(base_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        subdir_name = f"anonymization_{timestamp}_{unique_id}"
        output_dir = base_dir_path / subdir_name
        
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created output directory: {output_dir}")
            return output_dir
        except Exception as e:
            self.logger.error(f"Failed to create output directory: {str(e)}")
            raise

    def _generate_fake_data(self, original_data: str, entity_type: str) -> str:
        """
        Generate fake data that matches the structure of the original sensitive data.
        
        Args:
            original_data: The original sensitive data to be replaced.
            entity_type: The type of entity (e.g., 'PERSON', 'EMAIL', etc.).
            
        Returns:
            str: Generated fake data matching the structure of the original.
        """
        if entity_type == "EMAIL_ADDRESS":
            local_part = ''.join(random.choices(string.ascii_lowercase, k=8))
            domain = ''.join(random.choices(string.ascii_lowercase, k=6))
            return f"{local_part}@{domain}.com"
        
        elif entity_type == "US_SSN":
            # Generate a random SSN that maintains the same format
            area = ''.join(random.choices(string.digits, k=3))
            group = ''.join(random.choices(string.digits, k=2))
            serial = ''.join(random.choices(string.digits, k=4))
            return f"{area}-{group}-{serial}"
        
        # For other types, maintain the structure including spaces and punctuation
        result = ""
        if original_data.lower()!="email":
            for char in original_data:
                if char.isalpha():
                    result += random.choice(string.ascii_letters)
                elif char.isdigit():
                    result += random.choice(string.digits)
                else:
                    result += char
        else:
            result=original_data
        return result

    def anonymize_text(
        self,
        input_content: Union[str, Path],
        output_base_directory: Union[str, Path],
        original_file_name_for_output: Optional[str] = None
    ) -> Tuple[Path, Path]:
        """
        Anonymizes the given text content or file, replacing sensitive data with plausible fakes.

        Args:
            input_content: The textual input, which can be either a file path (str or Path)
                           or the direct content of the text (str).
            output_base_directory: The base directory where anonymized files and CSV will be saved.
                                   A new subdirectory will be created within this for each call.
            original_file_name_for_output: Optional string to use as the base name for output files.
                                           If input_content is a file path and this is None,
                                           it will be derived from the input file's name.

        Returns:
            A tuple containing:
            - Path to the generated anonymized text file.
            - Path to the sensitive data mapping CSV file.
        """
        self.logger.info(f"Starting anonymization process")
        
        # Generate unique ID for this anonymization session
        unique_id = self._generate_unique_id()
        
        # Create output subdirectory
        output_dir = self._create_output_subdirectory(output_base_directory, unique_id)
        
        # Handle input content and determine original file name
        try:
            if isinstance(input_content, (str, Path)) and Path(input_content).is_file():
                input_path = Path(input_content)
                with open(input_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                original_file_name = original_file_name_for_output or input_path.stem
            else:
                text_content = str(input_content)
                original_file_name = (original_file_name_for_output or 
                                    f"no_filename_provided_{unique_id}")
            
            # Clean the original file name
            original_file_name = "".join(c if c.isalnum() else "_" for c in original_file_name)
            self.logger.info(f"Using base name '{original_file_name}' for output files")
            
        except Exception as e:
            self.logger.error(f"Failed to process input content: {str(e)}")
            raise

        # Initialize mapping dictionary and analyze text
        original_to_generated_map: Dict[str, str] = {}
        
        try:
            # Analyze text for sensitive data
            analyzer_results = self.analyzer.analyze(text=text_content,
                                                  language='en')
            self.logger.info(f"Identified {len(analyzer_results)} potential sensitive data instances")
            
            # Create and write to CSV file
            csv_path = output_dir / f"sensitive_data_{original_file_name}_{unique_id}.csv"
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['sensitive_data_original', 'sensitive_data_generated'])
                
                # Process each sensitive data instance
                for result in analyzer_results:
                    original = text_content[result.start:result.end]
                    if original not in original_to_generated_map:
                        # Try to generate fake data up to 3 times
                        for attempt in range(3):
                            try:
                                generated = self._generate_fake_data(original, result.entity_type)
                                original_to_generated_map[original] = generated
                                writer.writerow([original, generated])
                                self.logger.info(
                                    f"Generated fake data for entity type {result.entity_type}")
                                break
                            except Exception as e:
                                if attempt == 2:
                                    self.logger.error(
                                        f"Failed to generate fake data after 3 attempts: {str(e)}")
                
            # Replace sensitive data in text
            anonymized_text = text_content
            for original, generated in original_to_generated_map.items():
                anonymized_text = anonymized_text.replace(original, generated)
            
            # Save anonymized text
            output_path = output_dir / f"anonymized_{original_file_name}_{unique_id}.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(anonymized_text)
            
            self.logger.info(f"Successfully saved anonymized text to {output_path}")
            return output_path, csv_path
            
        except Exception as e:
            self.logger.error(f"Error during anonymization process: {str(e)}")
            raise

    def deanonymize_text(
        self,
        anonymized_file_path: Union[str, Path],
        output_base_directory: Union[str, Path]
    ) -> Path:
        """
        De-anonymizes the given anonymized text file using its corresponding sensitive data mapping.

        Args:
            anonymized_file_path: The path to the anonymized text file.
            output_base_directory: The base directory where the de-anonymized file will be saved.
                                   The corresponding sensitive_data CSV will be found here.

        Returns:
            Path to the de-anonymized file.
        """
        self.logger.info("Starting de-anonymization process")
        
        try:
            # Convert paths to Path objects
            anonymized_path = Path(anonymized_file_path)
            output_base_path = Path(output_base_directory)
            
            # Extract file name components
            file_name_parts = anonymized_path.stem.split('_')
            original_name_parts = file_name_parts[1:-1]  # Skip 'anonymized_' and the unique ID
            unique_id = file_name_parts[-1]
            original_file_name = '_'.join(original_name_parts)
            
            # Find the corresponding CSV file
            csv_path = anonymized_path.parent / f"sensitive_data_{original_file_name}_{unique_id}.csv"
            
            if not csv_path.exists():
                raise FileNotFoundError(f"Sensitive data mapping file not found: {csv_path}")
            
            # Load the sensitive data mapping
            generated_to_original_map: Dict[str, str] = {}
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    generated_to_original_map[row['sensitive_data_generated']] = \
                        row['sensitive_data_original']
            
            # Load and process the anonymized text
            with open(anonymized_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # Replace generated data with original data
            deanonymized_text = text_content
            for generated, original in generated_to_original_map.items():
                deanonymized_text = deanonymized_text.replace(generated, original)
            
            # Save de-anonymized text
            output_path = anonymized_path.parent / \
                f"deanonymized_{original_file_name}_{unique_id}.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(deanonymized_text)
            
            self.logger.info(f"Successfully saved de-anonymized text to {output_path}")
            
            # Delete the CSV file
            csv_path.unlink()
            self.logger.info(f"Deleted sensitive data mapping file: {csv_path}")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error during de-anonymization process: {str(e)}")
            raise
