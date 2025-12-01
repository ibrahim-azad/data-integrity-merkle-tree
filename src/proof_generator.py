"""
Authentication Path Generation Module
Generates and validates cryptographic proofs for record existence
Refactored Implementation - 2024
"""

import json
import os
import datetime
import time
from crypto_hash_tree import IntegrityTreeStructure


def locate_and_verify_record(parameters):
    """
    Main entry point for record search and authentication proof generation
    
    Searches for a specific record by ID, generates authentication path,
    and validates the path against stored apex hash
    
    Args:
        parameters: Command-line arguments [dataset_name, record_id]
    """
    # Validate input parameters
    if len(parameters) != 2:
        print("Usage: locate [DatasetName] [recordID]")
        return
    
    dataset_identifier = parameters[0]
    target_record_id = parameters[1]

    print(f'Search Query: Record ID = "{target_record_id}"')
    print("\nInitiating tree search operation...")

    # Construct path to processed dataset
    processed_data_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'data', 
        'processed', 
        f'{dataset_identifier}_proc.json'
    )
    
    if not os.path.exists(processed_data_path):
        print(f"Processed dataset file not located: {processed_data_path}")
        return

    # Load processed dataset
    try:
        with open(processed_data_path, 'r', encoding='utf-8') as data_file:
            record_collection = json.load(data_file)
    except Exception as load_error:
        print(f"Error during data loading: {load_error}")
        return

    # Search for target record in dataset
    target_record = None
    for record in record_collection:
        if record.get('ReviewID') == target_record_id:
            target_record = record
            break
    
    if not target_record:
        print(f"Record with ReviewID {target_record_id} not found in dataset.")
        return

    print("✓ Record successfully located in dataset")

    print("\nRetrieving stored apex hash...")
    
    # Retrieve stored apex hash from disk
    apex_storage_dir = os.path.join(os.path.dirname(__file__), 'roots')
    stored_apex_hash = None
    
    if os.path.exists(apex_storage_dir):
        # Find all root files for this dataset
        apex_file_list = [
            filename for filename in os.listdir(apex_storage_dir) 
            if filename.startswith(f'{dataset_identifier}_root_v') and filename.endswith('.json')
        ]
        
        if apex_file_list:
            version_mapping = []
            
            # Extract version numbers from filenames
            for filename in apex_file_list:
                try:
                    version_segment = filename.split('_root_v')[1].split('.json')[0]
                    version_number = float(version_segment)
                    version_mapping.append((version_number, filename))
                except ValueError:
                    continue
            
            if version_mapping:
                # Get most recent version
                most_recent_file = max(version_mapping, key=lambda x: x[0])[1]
                apex_file_path = os.path.join(apex_storage_dir, most_recent_file)
                
                with open(apex_file_path, 'r', encoding='utf-8') as apex_file:
                    apex_metadata = json.load(apex_file)
                    stored_apex_hash = apex_metadata.get("root_hash")

    if not stored_apex_hash:
        print("No stored apex hash found for dataset.")
        return

    # Build tree structure and generate proof
    print("\nConstructing authentication proof...")
    
    hash_tree = IntegrityTreeStructure()
    hash_tree.build_complete_tree(record_collection)
  
    verification_start = time.time()

    # Generate authentication path for target record
    authentication_path = hash_tree.create_verification_path(target_record_id)
    
    if authentication_path is None:
        print("Authentication path generation failed.")
        return

    # Display authentication path details
    print(f"\nAuthentication Path ({len(authentication_path)} steps):")
    step_number = 1
    for direction_indicator, sibling_digest in authentication_path:
        print(f"  Step {step_number}:  [{direction_indicator}] Sibling: {sibling_digest[:16]}...")
        step_number += 1

    # Verify authentication path
    print("\nValidating authentication path...")
    
    # Start with terminal vertex hash
    terminal_hash = hash_tree.generate_record_hash(target_record)
    print(f"✓ Terminal hash: {terminal_hash[:16]}...")
    
    # Recompute apex by traversing path
    recomputed_apex = terminal_hash
    for direction_indicator, sibling_digest in authentication_path:
        if direction_indicator == "LEFT":
            recomputed_apex = hash_tree.combine_child_hashes(recomputed_apex, sibling_digest)
        else:
            recomputed_apex = hash_tree.combine_child_hashes(sibling_digest, recomputed_apex)
    
    verification_end = time.time()
    verification_duration = (verification_end - verification_start) * 1000
    
    print(f"✓ Recomputed apex: {recomputed_apex[:16]}...")
    print(f"✓ Stored apex: {stored_apex_hash[:16]}...")
    
    # Compare hashes
    match_indicator = "✓ YES" if recomputed_apex == stored_apex_hash else "✗ NO"
    print(f"✓ Apex hashes MATCH: {match_indicator}")

    # Display final result
    if recomputed_apex == stored_apex_hash:
        print("\nVerification Result: ✓ AUTHENTICATED - Record exists in dataset")
    else:
        print("\nVerification Result: ✗ AUTHENTICATION FAILED - Record absent or tree corrupted")

    # Display proof metrics
    print("\nAuthentication Proof Metrics:")
    print(f"- Path length: {len(authentication_path)} hash operations")
    print(f"- Verification duration: {verification_duration:.3f} ms")
    print("- Memory consumption: N/A")  # Complex to measure accurately
