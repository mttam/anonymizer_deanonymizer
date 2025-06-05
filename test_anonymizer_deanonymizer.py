import unittest
from pathlib import Path
from anonymizer_deanonymizer import AnonymizerDeAnonymizer

class TestAnonymizerDeAnonymizer(unittest.TestCase):
    def setUp(self):
        self.anonymizer = AnonymizerDeAnonymizer()
        self.test_dir = Path(__file__).parent / "test_output"
        self.test_dir.mkdir(exist_ok=True)

    def test_anonymization_and_deanonymization(self):
        # Test text with sensitive information
        test_text = """
        Patient Name: John Smith
        Email: john.smith@email.com
        SSN: 123-45-6789
        Credit Card: 4111-1111-1111-1111
        Medical History: Patient has diabetes and high blood pressure.
        """

        # Test anonymization
        anonymized_path, csv_path = self.anonymizer.anonymize_text(
            test_text,
            self.test_dir,
            "test_patient_record"
        )

        # Verify files were created
        self.assertTrue(anonymized_path.exists())
        self.assertTrue(csv_path.exists())

        # Read anonymized content
        with open(anonymized_path, 'r') as f:
            anonymized_content = f.read()

        # Verify sensitive data was replaced
        self.assertNotIn("John Smith", anonymized_content)
        self.assertNotIn("john.smith@email.com", anonymized_content)
        self.assertNotIn("123-45-6789", anonymized_content)
        self.assertNotIn("4111-1111-1111-1111", anonymized_content)

        # Test de-anonymization
        deanonymized_path = self.anonymizer.deanonymize_text(
            anonymized_path,
            self.test_dir
        )

        # Verify de-anonymized content matches original
        with open(deanonymized_path, 'r') as f:
            deanonymized_content = f.read()

        self.assertEqual(test_text.strip(), deanonymized_content.strip())
        
        # Verify CSV was deleted after de-anonymization
        self.assertFalse(csv_path.exists())

if __name__ == '__main__':
    unittest.main()
