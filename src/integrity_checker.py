"""
Data Integrity Verification Module
Validates dataset integrity by comparing stored vs. current apex hashes
Refactored Implementation - 2024
"""

import json
import os
import datetime
import time
from crypto_hash_tree import IntegrityTreeStructure


def execute_integrity_check(parameters):
    """
    Main entry point for dataset integrity verification
    
    Compares current dataset apex hash against previously stored hash
    to detect any unauthorized modifications
    
    Args:
        parameters: Command-line arguments [dataset_name]
    """
    # Validate input
    if len(parameters) != 1:
        print("Usage: check-integrity [DataSetName]")
        return
    
    dataset_identifier = parameters[0]

    # Load stored apex hash and metadata
    apex_storage_directory = os.path.join(os.path.dirname(__file__), 'roots')
    stored_apex_digest = None
    stored_metadata = None
    apex_file_location = None
    
    if os.path.exists(apex_storage_directory):
        # Find all apex files for dataset
        apex_file_collection = [
            filename for filename in os.listdir(apex_storage_directory) 
            if filename.startswith(f'{dataset_identifier}_root_v') and filename.endswith('.json')
        ]
        
        if apex_file_collection:
            version_list = []
            
            # Parse version numbers from filenames
            for filename in apex_file_collection:
                try:
                    version_string = filename.split('_root_v')[1].split('.json')[0]
                    version_value = float(version_string)
                    version_list.append((version_value, filename))
                except ValueError:
                    pass
            
            if version_list:
                # Get latest version file
                latest_version_file = max(version_list, key=lambda x: x[0])[1]
                apex_file_location = os.path.join(apex_storage_directory, latest_version_file)
                
                with open(apex_file_location, 'r', encoding='utf-8') as metadata_file:
                    stored_metadata = json.load(metadata_file)
                    stored_apex_digest = stored_metadata.get("root_hash")

    if not stored_apex_digest:
        print("No stored apex hash found for dataset.")
        return

    print("Retrieving stored apex hash...")
    print(f"✓ Loaded from location: {apex_file_location}")

    # Extract stored metadata details
    stored_creation_time = stored_metadata.get("timestamp", "Unknown")
    if stored_creation_time != "Unknown":
        try:
            stored_creation_time = datetime.datetime.fromisoformat(stored_creation_time).strftime("%d-%m-%y %H:%M:%S")
        except ValueError:
            pass
    
    stored_entry_count = stored_metadata.get("record_count", 0)
    stored_dataset_name = stored_metadata.get("dataset", dataset_identifier)

    # Display stored apex information
    print("\nStored Apex Metadata:")
    print(f"  Creation Time: {stored_creation_time}")
    print(f"  Apex Hash: {stored_apex_digest}")
    print(f"  Entry Count: {stored_entry_count:,}")
    print(f"  Dataset: {stored_dataset_name}")

    # Load current processed dataset
    processed_data_file = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'data', 
        'processed', 
        f'{dataset_identifier}_proc.json'
    )
    
    if not os.path.exists(processed_data_file):
        print(f"Processed dataset file not found: {processed_data_file}")
        return

    # Read dataset records
    try:
        with open(processed_data_file, 'r', encoding='utf-8') as data_file:
            current_record_set = json.load(data_file)
    except Exception as read_error:
        print(f"Error reading processed dataset: {read_error}")
        return

    # Build current tree and compute apex
    print("\nConstructing current tree structure...")
    
    verification_tree = IntegrityTreeStructure()
    current_apex_digest, _ = verification_tree.build_complete_tree(current_record_set)
    current_verification_time = datetime.datetime.now().strftime("%d-%m-%y %H:%M:%S")
    current_entry_count = len(current_record_set)

    print("✓ Current apex hash computed")

    # Display current tree information
    print("\nCurrent Tree Metadata:")
    print(f"  Verification Time: {current_verification_time}")
    print(f"  Apex Hash: {current_apex_digest}")
    print(f"  Entry Count: {current_entry_count:,}")

    # Perform apex comparison
    print("\nIntegrity Verification Result:")
    print(f"  Stored:  {stored_apex_digest}")
    print(f"  Current: {current_apex_digest}")
    
    match_status = "✓ YES" if stored_apex_digest == current_apex_digest else "✗ NO"
    print(f"  Match: {match_status}")

    # Display final verdict
    if stored_apex_digest == current_apex_digest:
        print("\n✓ DATA INTEGRITY CONFIRMED")
        print(f"No tampering detected since {stored_creation_time}")
    else:
        print("\n⚠ DATA INTEGRITY COMPROMISED")
        print(f"Dataset has been altered since {stored_creation_time}")
