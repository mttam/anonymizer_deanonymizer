import unittest
from pathlib import Path
from anonymizer_deanonymizer import AnonymizerDeAnonymizer
import shutil

class TestAnonymizerDeAnonymizer(unittest.TestCase):
    def setUp(self):
        self.anonymizer = AnonymizerDeAnonymizer()
        self.test_dir = Path(__file__).parent / "test_output"
        self.test_dir.mkdir(exist_ok=True)

    def simulate_model_response(self, anonymized_prompt: str) -> str:
        """
        Simulate a language model's response that references the anonymized entities.
        The model response will contain the same anonymized placeholders.
        """
        response = f"""
        Based on the patient information provided, I can offer the following medical advice:
        
        The patient profile shows important health conditions that require monitoring.
        For the patient referenced in your query, please ensure:
        
        1. Regular follow-up appointments are scheduled
        2. Contact information remains current for communication
        3. All medical records are properly maintained
        
        Patient Summary:
        - The individual mentioned appears to have chronic conditions
        - Contact details should be verified for accuracy
        - Financial information has been noted for billing purposes
        
        Please maintain confidentiality of all patient data throughout the treatment process.
        
        Original request reference:
        {anonymized_prompt}
        """
        return response

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

    def test_complete_workflow_with_model_response_deanonymization(self):
        """
        Test the complete workflow including de-anonymizing the model's response.
        This simulates: anonymize prompt -> send to model -> get response -> de-anonymize both prompt and response
        """
        # Test text with sensitive information
        test_text = """
        Patient Name: Sarah Johnson
        Email: sarah.johnson@hospital.com
        SSN: 987-65-4321
        Phone: 555-123-4567
        Credit Card: 5555-5555-5555-4444
        Medical History: Patient has hypertension and requires regular monitoring.
        Please schedule follow-up with Sarah Johnson at sarah.johnson@hospital.com.
        """

        # Step 1: Anonymize the original prompt
        anonymized_path, csv_path = self.anonymizer.anonymize_text(
            test_text,
            self.test_dir,
            "patient_consultation"
        )

        # Read anonymized content
        with open(anonymized_path, 'r') as f:
            anonymized_content = f.read()

        # Verify sensitive data was anonymized
        self.assertNotIn("Sarah Johnson", anonymized_content)
        self.assertNotIn("sarah.johnson@hospital.com", anonymized_content)
        self.assertNotIn("987-65-4321", anonymized_content)
        self.assertNotIn("555-123-4567", anonymized_content)

        # Step 2: Simulate model response (model receives anonymized prompt)
        model_response = self.simulate_model_response(anonymized_content)
        
        # Save model response to file
        model_response_path = self.test_dir / f"model_response_{anonymized_path.stem}.txt"
        with open(model_response_path, 'w') as f:
            f.write(model_response)

        # Step 3: IMPORTANT - Create backup of CSV mapping BEFORE de-anonymizing anything
        csv_backup_path = self.test_dir / f"backup_{csv_path.name}"
        shutil.copy2(csv_path, csv_backup_path)

        # Step 4: De-anonymize the original prompt (this will delete the CSV file)
        deanonymized_prompt_path = self.anonymizer.deanonymize_text(
            anonymized_path,
            self.test_dir
        )

        # Step 5: Manually create the expected CSV path for model response de-anonymization
        # The de-anonymization expects a specific naming pattern
        expected_csv_name = f"sensitive_data_{model_response_path.stem}.csv"
        expected_csv_path = self.test_dir / expected_csv_name
        
        # Copy the backup to the expected location
        shutil.copy2(csv_backup_path, expected_csv_path)

        # Step 6: Create an anonymized version of the model response file with expected naming
        # The de-anonymization expects the file to start with "anonymized_"
        model_response_anonymized_path = self.test_dir / f"anonymized_{model_response_path.stem}.txt"
        shutil.copy2(model_response_path, model_response_anonymized_path)

        # Step 7: De-anonymize the model response
        deanonymized_model_response_path = self.anonymizer.deanonymize_text(
            model_response_anonymized_path,
            self.test_dir
        )

        # Step 8: Verify results
        # Check that original prompt was properly de-anonymized
        with open(deanonymized_prompt_path, 'r') as f:
            deanonymized_prompt = f.read()
        
        self.assertIn("Sarah Johnson", deanonymized_prompt)
        self.assertIn("sarah.johnson@hospital.com", deanonymized_prompt)
        self.assertIn("987-65-4321", deanonymized_prompt)

        # Check that model response was properly de-anonymized
        with open(deanonymized_model_response_path, 'r') as f:
            deanonymized_model_response = f.read()

        # The de-anonymized model response should contain the original sensitive data
        # where the model referenced the anonymized entities
        self.assertIn("Sarah Johnson", deanonymized_model_response)
        self.assertIn("sarah.johnson@hospital.com", deanonymized_model_response)

        print(f"\n🔍 Original prompt de-anonymized: {deanonymized_prompt_path.name}")
        print(f"🤖 Model response de-anonymized: {deanonymized_model_response_path.name}")
        print(f"📁 All files in: {self.test_dir}")

        # Clean up backup file
        if csv_backup_path.exists():
            csv_backup_path.unlink()

    def test_end_to_end_anonymization_workflow(self):
        """
        Complete end-to-end test: anonymize -> model simulation -> de-anonymize response
        """
        # Original sensitive prompt
        sensitive_prompt = """
        Customer: Maria Garcia
        Email: maria.garcia@email.com  
        Phone: 555-987-6543
        Account: ACC-123456789
        
        Issue: Customer Maria Garcia (maria.garcia@email.com) is asking about 
        her recent charge of $1,250.00. Please call her back at 555-987-6543.
        """

        # Step 1: Anonymize the prompt
        anonymized_path, csv_path = self.anonymizer.anonymize_text(
            sensitive_prompt,
            self.test_dir,
            "customer_service_request"
        )

        with open(anonymized_path, 'r') as f:
            anonymized_content = f.read()

        # Step 2: Simulate model response that includes the anonymized content
        model_response = f"""
        Dear Customer Service Team,
        
        Regarding the customer inquiry in your request:
        
        I recommend the following actions for the customer mentioned:
        1. Review the account history for the specified account number
        2. Verify the charge amount mentioned in the inquiry
        3. Contact the customer using the provided phone number
        4. Send a follow-up email to the customer's email address
        
        The customer appears to have a legitimate concern that should be addressed promptly.
        Please ensure all communication maintains our professional standards.
        
        Original anonymized request for reference:
        {anonymized_content}
        """

        # Step 3: Save model response
        model_response_path = self.test_dir / "model_response_customer_service.txt"
        with open(model_response_path, 'w') as f:
            f.write(model_response)

        # Step 4: Backup CSV before de-anonymizing prompt
        csv_backup_path = self.test_dir / f"backup_{csv_path.name}"
        shutil.copy2(csv_path, csv_backup_path)

        # Step 5: De-anonymize the original prompt
        deanonymized_prompt_path = self.anonymizer.deanonymize_text(
            anonymized_path,
            self.test_dir
        )

        # Step 6: Prepare model response for de-anonymization with correct naming
        model_anonymized_path = self.test_dir / f"anonymized_{model_response_path.stem}.txt"
        shutil.copy2(model_response_path, model_anonymized_path)
        
        # Create CSV mapping for model response with expected naming pattern
        model_csv_path = self.test_dir / f"sensitive_data_{model_response_path.stem}.csv"
        shutil.copy2(csv_backup_path, model_csv_path)

        # Step 7: De-anonymize the model response
        deanonymized_model_response_path = self.anonymizer.deanonymize_text(
            model_anonymized_path,
            self.test_dir
        )

        # Step 8: Verify the de-anonymized content contains original sensitive data
        with open(deanonymized_prompt_path, 'r') as f:
            final_prompt = f.read()

        with open(deanonymized_model_response_path, 'r') as f:
            final_model_response = f.read()

        # Assertions
        self.assertIn("Maria Garcia", final_prompt)
        self.assertIn("maria.garcia@email.com", final_prompt)
        self.assertIn("555-987-6543", final_prompt)

        # Model response should also contain de-anonymized data since it included the anonymized content
        self.assertIn("Maria Garcia", final_model_response)
        self.assertIn("maria.garcia@email.com", final_model_response)

        print(f"\n✅ End-to-end test completed!")
        print(f"📄 Original prompt de-anonymized: {deanonymized_prompt_path.name}")
        print(f"🤖 Model response de-anonymized: {deanonymized_model_response_path.name}")
        print(f"📂 All files saved in: {self.test_dir}")

        # Clean up backup file
        if csv_backup_path.exists():
            csv_backup_path.unlink()

if __name__ == '__main__':
    unittest.main(verbosity=2)
