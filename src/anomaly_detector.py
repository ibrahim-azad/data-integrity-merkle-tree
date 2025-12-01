"""
Tampering Detection Module
Simulates various data tampering scenarios and validates detection capabilities
Refactored Implementation - 2024
"""

import json
import os
import datetime
import time
import random
import string
from crypto_hash_tree import IntegrityTreeStructure


def run_tampering_detection(parameters):
    """
    Main entry point for tampering detection simulation
    
    Executes N tampering simulations of specified type and validates
    detection through apex hash comparison
    
    Args:
        parameters: [dataset_name, action_type, simulation_count]
                   action_type: --insert, --modify, or --delete
    """
    # Validate command parameters
    if len(parameters) != 3:
        print("Usage: detect-tampering [datasetName] [action] [N]")
        return
    
    dataset_identifier = parameters[0]
    tampering_action = parameters[1]
    
    if tampering_action not in ["--insert", "--modify", "--delete"]:
        print("Invalid action. Valid options: --insert, --modify, --delete")
        return
    
    try:
        simulation_iterations = int(parameters[2])
        if simulation_iterations < 1:
            print("Simulation count N must be at least 1")
            return
    except ValueError:
        print("N must be integer value")
        return

    # Load original processed dataset
    processed_dataset_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'data', 
        'processed', 
        f'{dataset_identifier}_proc.json'
    )
    
    if not os.path.exists(processed_dataset_path):
        print(f"Processed dataset not located: {processed_dataset_path}")
        return

    # Read dataset records
    try:
        with open(processed_dataset_path, 'r', encoding='utf-8') as dataset_file:
            baseline_records = json.load(dataset_file)
    except Exception as load_error:
        print(f"Error loading dataset: {load_error}")
        return

    # Retrieve baseline apex hash
    apex_directory = os.path.join(os.path.dirname(__file__), 'roots')
    baseline_apex_hash = None
    
    if os.path.exists(apex_directory):
        apex_files = [
            f for f in os.listdir(apex_directory) 
            if f.startswith(f'{dataset_identifier}_root_v') and f.endswith('.json')
        ]
        
        if apex_files:
            version_data = []
            
            for apex_filename in apex_files:
                try:
                    version_str = apex_filename.split('_root_v')[1].split('.json')[0]
                    version_num = float(version_str)
                    version_data.append((version_num, apex_filename))
                except ValueError:
                    pass
            
            if version_data:
                latest_apex_file = max(version_data, key=lambda x: x[0])[1]
                apex_filepath = os.path.join(apex_directory, latest_apex_file)
                
                try:
                    with open(apex_filepath, 'r', encoding='utf-8') as apex_file:
                        apex_metadata = json.load(apex_file)
                        baseline_apex_hash = apex_metadata.get("root_hash")
                except Exception:
                    pass

    if not baseline_apex_hash:
        print("No baseline apex hash found.")
        return

    # Execute tampering simulations
    iteration_number = 0
    while iteration_number < simulation_iterations:
        print(f"\nSimulation {iteration_number + 1}/{simulation_iterations}")

        # Create working copy of records
        tampered_records = [record.copy() for record in baseline_records]

        # Apply tampering based on action type
        if tampering_action == "--insert":
            # Generate new record with unique ID
            existing_id_numbers = [
                int(rec['ReviewID'][1:]) for rec in tampered_records 
                if rec.get('ReviewID', '').startswith('R')
            ]
            next_id_number = max(existing_id_numbers) + 1 if existing_id_numbers else 0
            new_record_id = f"R{next_id_number:06d}"

            # Generate random reviewer and product identifiers
            random_reviewer_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=13))
            random_product_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            
            # Generate timestamp data
            current_datetime = datetime.datetime.now()
            formatted_review_time = current_datetime.strftime("%m %d, %Y")
            unix_timestamp = int(time.time())

            # Construct new review record
            fabricated_record = {
                "ReviewID": new_record_id,
                "reviewerID": random_reviewer_id,
                "asin": random_product_id,
                "overall": round(random.uniform(1.0, 5.0), 1),
                "vote": str(random.randint(0, 100)),
                "verified": random.choice([True, False]),
                "reviewTime": formatted_review_time,
                "reviewerName": f"User{random.randint(1, 1000)}",
                "reviewText": f"Random review content {random.randint(1, 100)}",
                "summary": f"Summary text {random.randint(1, 100)}",
                "unixReviewTime": unix_timestamp,
                "style": {}
            }
            
            tampered_records.append(fabricated_record)
            print("Executing tampering simulation...")
            print(f"Inserted: Record #{new_record_id}")

        elif tampering_action == "--delete":
            if not tampered_records:
                print("No records available for deletion")
                iteration_number += 1
                continue
            
            target_record = random.choice(tampered_records)
            target_id = target_record['ReviewID']
            tampered_records.remove(target_record)
            
            print("Executing tampering simulation...")
            print(f"Deleted: Record #{target_id}")

        elif tampering_action == "--modify":
            if not tampered_records:
                print("No records available for modification")
                iteration_number += 1
                continue
            
            target_record = random.choice(tampered_records)
            target_id = target_record['ReviewID']
            
            # Select random field to modify
            modifiable_fields = ["overall", "vote", "reviewerName", "reviewText", "summary"]
            selected_field = random.choice(modifiable_fields)
            original_field_value = str(target_record.get(selected_field, ""))
            
            # Apply modification based on field type
            if selected_field == "overall":
                target_record[selected_field] = round(random.uniform(1.0, 5.0), 1)
            elif selected_field == "vote":
                target_record[selected_field] = str(random.randint(0, 100))
            else:
                target_record[selected_field] = f"Modified {selected_field} {random.randint(1, 100)}"
            
            print("Executing tampering simulation...")
            print(f"Modified: Record #{target_id}")
            print(f"Field: {selected_field}")
            print(f"Original: \"{original_field_value}\"")
            print(f"Modified: \"{target_record[selected_field]}\"")

        # Rebuild tree with tampered data
        print("\nReconstructing tree structure...")
        
        tampered_tree = IntegrityTreeStructure()
        rebuild_start = time.time()
        tampered_apex_hash, _ = tampered_tree.build_complete_tree(tampered_records)
        rebuild_end = time.time()
        rebuild_duration = (rebuild_end - rebuild_start) * 1000
        
        print(f"Tampered apex computed: {tampered_apex_hash[:16]}...")

        # Compare apex hashes
        print("\nApex Hash Comparison:")
        print(f"  Baseline: {baseline_apex_hash[:32]}...")
        print(f"  Tampered: {tampered_apex_hash[:32]}...")
        
        match_indicator = "✓ YES" if tampered_apex_hash == baseline_apex_hash else "✗ NO"
        print(f"  Match: {match_indicator}")

        # Display detection result
        if tampered_apex_hash != baseline_apex_hash:
            print("⚠ TAMPERING DETECTED")
            print(f"[Detection Time: {rebuild_duration:.3f} ms]")

            # Calculate tampering statistics
            baseline_count = len(baseline_records)
            tampered_count = len(tampered_records)
            affected_records = abs(tampered_count - baseline_count) if tampering_action in ["--insert", "--delete"] else 1
            
            tampering_type_map = {
                "--insert": "Insertion", 
                "--delete": "Deletion", 
                "--modify": "Modification"
            }
            detected_type = tampering_type_map[tampering_action]
            
            print("\nTampering Analysis:")
            print(f"- Affected records: {affected_records}")
            print(f"- {detected_type} detected")
            print("- Modifications prevented")
        else:
            print("No tampering detected")

        iteration_number += 1
