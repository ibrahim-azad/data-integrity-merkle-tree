"""
Dataset Modification Module
Handles insertion, modification, and deletion of records in processed datasets
Refactored Implementation - 2024
"""

import json
import os
import datetime
import time
import random
import string
from crypto_hash_tree import IntegrityTreeStructure


def perform_dataset_update(parameters):
    """
    Main entry point for dataset modification operations
    
    Supports three modification types:
    - Insert: Add new record with auto-generated IDs
    - Modify: Update existing record fields
    - Delete: Remove record with confirmation
    
    Args:
        parameters: [dataset_name, action, record_id]
                   record_id optional for --insert action
    """
    # Validate parameters
    if len(parameters) < 2:
        print("Usage: modify [DatasetName] [Action] [recordID]")
        print("For --insert operation, recordID is not required.")
        return
    
    dataset_identifier = parameters[0]
    modification_action = parameters[1]
    
    if modification_action not in ["--insert", "--modify", "--delete"]:
        print("Invalid action. Valid options: --insert, --modify, --delete")
        return
    
    # Extract record ID (not needed for insert)
    if modification_action == "--insert":
        target_record_id = None
    else:
        if len(parameters) < 3:
            print("Usage: modify [DatasetName] [Action] [recordID]")
            return
        target_record_id = parameters[2]

    # Locate processed dataset file
    processed_file_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'data', 
        'processed', 
        f'{dataset_identifier}_proc.json'
    )
    
    if not os.path.exists(processed_file_path):
        print(f"Processed dataset not found: {processed_file_path}")
        return

    # Load dataset records
    try:
        with open(processed_file_path, 'r', encoding='utf-8') as dataset_file:
            record_collection = json.load(dataset_file)
    except Exception as read_error:
        print(f"Error loading dataset: {read_error}")
        return

    # Execute modification based on action type
    if modification_action == "--insert":
        # Generate unique record ID
        id_number_list = [
            int(rec['ReviewID'][1:]) for rec in record_collection 
            if 'ReviewID' in rec and rec['ReviewID'].startswith('R')
        ]
        next_id_value = max(id_number_list) + 1 if id_number_list else 0
        generated_record_id = f"R{next_id_value:06d}"

        # Generate random reviewer identifier (13 alphanumeric characters)
        generated_reviewer_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=13))

        # Generate random product ASIN (10 alphanumeric characters)
        generated_asin = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        # Generate current timestamps
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%m %d, %Y")
        unix_time_value = int(time.time())

        # Initialize new record with default values
        new_record_data = {
            "ReviewID": generated_record_id,
            "reviewerID": generated_reviewer_id,
            "asin": generated_asin,
            "overall": 0.0,
            "vote": "",
            "verified": False,
            "reviewTime": formatted_time,
            "reviewerName": "",
            "reviewText": "",
            "summary": "",
            "unixReviewTime": unix_time_value,
            "style": {}
        }

        # Collect user input for modifiable fields
        # Overall rating
        while True:
            try:
                overall_input = input("Enter overall rating (float, e.g. 4.5): ").strip()
                if overall_input == "":
                    new_record_data["overall"] = 0.0
                else:
                    new_record_data["overall"] = float(overall_input)
                break
            except ValueError:
                print("Invalid float value. Please try again.")

        # Vote count
        new_record_data["vote"] = input("Enter vote count (string): ").strip()

        # Reviewer name
        new_record_data["reviewerName"] = input("Enter reviewer name: ").strip()

        # Review text content
        new_record_data["reviewText"] = input("Enter review text content: ").strip()

        # Review summary
        new_record_data["summary"] = input("Enter summary: ").strip()

        record_collection.append(new_record_data)
        print(f"Inserted new record with ReviewID: {generated_record_id}")

    elif modification_action == "--modify":
        # Locate target record
        target_record = None
        for rec in record_collection:
            if rec.get('ReviewID') == target_record_id:
                target_record = rec
                break
        
        if not target_record:
            print(f"Record with ReviewID {target_record_id} not found.")
            return
        
        # Define field mapping for user-friendly input
        field_mapping = {
            "overall": "overall",
            "vote": "vote",
            "name": "reviewerName",
            "reviewtext": "reviewText",
            "review_text": "reviewText",
            "summary": "summary"
        }
        
        print("Modifiable fields: overall, vote, name, reviewText, summary")
        field_input = input("Enter field to modify: ").strip().lower().replace(" ", "").replace("-", "")
        
        mapped_field = field_mapping.get(field_input)
        if not mapped_field:
            print("Field not modifiable.")
            return
        
        print(f"Current value: {target_record.get(mapped_field, '')}")
        
        # Handle different field types
        if mapped_field == "overall":
            while True:
                try:
                    new_value = input("Enter new value (float): ").strip()
                    target_record[mapped_field] = float(new_value)
                    break
                except ValueError:
                    print("Invalid float value.")
        else:
            target_record[mapped_field] = input("Enter new value: ").strip()
        
        print(f"Modified {mapped_field} for ReviewID {target_record_id}")

    elif modification_action == "--delete":
        # Locate target record
        target_record = None
        for rec in record_collection:
            if rec.get('ReviewID') == target_record_id:
                target_record = rec
                break
        
        if not target_record:
            print(f"Record with ReviewID {target_record_id} not found.")
            return
        
        # Confirm deletion
        confirmation = input(f"Confirm deletion of ReviewID {target_record_id}? (yes/no): ").lower()
        if confirmation == "yes":
            record_collection.remove(target_record)
            print(f"Deleted ReviewID {target_record_id}")
        else:
            print("Deletion operation cancelled.")

    # Persist modified dataset
    print("\nPersisting dataset modifications...")
    try:
        with open(processed_file_path, 'w', encoding='utf-8') as output_file:
            json.dump(record_collection, output_file, indent=4, ensure_ascii=False)
    except Exception as write_error:
        print(f"Error persisting dataset: {write_error}")
        return
    
    print("✓ Dataset modifications saved.")
