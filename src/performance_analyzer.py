"""
Performance Analysis and Benchmarking Module
Executes comprehensive performance tests on hash tree operations
Refactored Implementation - 2024
"""

import json
import os
import datetime
import time
import random
import string
import tracemalloc
import psutil
from dataset_processor import ReviewDataImporter
from crypto_hash_tree import IntegrityTreeStructure


def initialize_dataset_and_tree(dataset_identifier="electronics", entry_limit=1000000):
    """
    Load dataset and construct hash tree for benchmarking
    
    Args:
        dataset_identifier: Name of dataset to load
        entry_limit: Maximum number of records to load
    
    Returns:
        Tuple: (records, tree, apex_hash, build_time, memory_peak)
        None values if operation fails
    """
    data_importer = ReviewDataImporter(dataset_identifier)
    
    try:
        record_data, import_stats = data_importer.load_and_process(entry_limit)
    except Exception as import_error:
        print(f"Dataset loading failed: {import_error}")
        return None, None, None, None, None
    
    if not record_data:
        print("No data loaded from dataset")
        return None, None, None, None, None

    # Debug output for data validation
    print(f"🔍 DEBUG: Loaded {len(record_data):,} reviews, avg size: {len(json.dumps(record_data[0]))} bytes")
    
    # Construct hash tree
    verification_tree = IntegrityTreeStructure()
    construction_start = time.time()
    apex_digest, peak_memory_usage = verification_tree.build_complete_tree(record_data)
    construction_duration = time.time() - construction_start
  
    if not apex_digest:
        print("Tree construction failed")
        return None, None, None, None, None
    
    return record_data, verification_tree, apex_digest, construction_duration, peak_memory_usage


def execute_proof_benchmarks(record_data, verification_tree, iteration_count=1000):
    """
    Benchmark authentication proof generation and verification
    
    Args:
        record_data: List of records
        verification_tree: Constructed hash tree
        iteration_count: Number of proof operations to benchmark
    
    Returns:
        Tuple: (average_time_ms, requirement_status, memory_usage_mb)
    """
    if len(record_data) < iteration_count:
        print(f"Insufficient data for {iteration_count} proof operations")
        return None, None, None

    timing_measurements = []
    iteration = 0
    
    while iteration < iteration_count:
        # Select random record
        random_record = random.choice(record_data)
        record_identifier = random_record['ReviewID']
        
        # Time proof generation and verification
        operation_start = time.time()
        
        authentication_path = verification_tree.create_verification_path(record_identifier)
        if authentication_path is None:
            iteration += 1
            continue
        
        # Verify proof by recomputing apex
        terminal_digest = verification_tree.generate_record_hash(random_record)
        recomputed_apex = terminal_digest
        
        for direction, sibling_hash in authentication_path:
            if direction == "LEFT":
                recomputed_apex = verification_tree.combine_child_hashes(recomputed_apex, sibling_hash)
            else:
                recomputed_apex = verification_tree.combine_child_hashes(sibling_hash, recomputed_apex)
        
        operation_end = time.time()
        timing_measurements.append((operation_end - operation_start) * 1000)
        iteration += 1

    # Calculate average timing
    average_duration = sum(timing_measurements) / len(timing_measurements) if timing_measurements else 0
    
    # Check against requirement threshold
    requirement_status = "✓ Met" if average_duration <= 100 else "✗ Not Met"
    
    # Measure current memory usage
    process_monitor = psutil.Process()
    current_memory_mb = process_monitor.memory_info().rss / 1024 / 1024
    
    return average_duration, requirement_status, current_memory_mb


def execute_static_benchmarks(record_data, verification_tree, construction_time, memory_peak):
    """
    Display static performance metrics from tree construction
    
    Args:
        record_data: List of records
        verification_tree: Constructed hash tree
        construction_time: Total tree build time in seconds
        memory_peak: Peak memory usage during construction in MB
    """
    # Calculate per-record hash time
    per_record_hash_time = construction_time / len(record_data) * 1000
    
    print(f"Per-Record Hash Time (avg): {per_record_hash_time:.6f} ms")
    print(f"Total Construction Time: {construction_time:.2f} seconds")
    print(f"Peak Memory Usage: {memory_peak:.2f} MB")


def execute_tampering_benchmarks(record_data, verification_tree, baseline_apex):
    """
    Benchmark tampering detection across multiple scenarios
    
    Args:
        record_data: Original record set
        verification_tree: Baseline tree structure
        baseline_apex: Original apex hash for comparison
    """
    tampering_scenarios = ["--insert", "--modify", "--delete"]
    total_simulations = 0
    successful_detections = 0
    timing_data = []

    for scenario_type in tampering_scenarios:
        print(f"\nScenario Type: {scenario_type}")
        
        scenario_iteration = 0
        while scenario_iteration < 5:
            print(f"\nSimulation {scenario_iteration + 1}")
            
            # Create mutable copy of dataset
            tampered_dataset = [rec.copy() for rec in record_data]
            
            if scenario_type == "--insert":
                # Generate unique ID for new record
                existing_id_values = [
                    int(r['ReviewID'][1:]) for r in tampered_dataset 
                    if r.get('ReviewID', '').startswith('R')
                ]
                new_id_number = max(existing_id_values) + 1 if existing_id_values else 0
                fabricated_review_id = f"R{new_id_number:06d}"
                
                # Generate random identifiers
                fabricated_reviewer = ''.join(random.choices(string.ascii_uppercase + string.digits, k=13))
                fabricated_asin = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                
                # Generate timestamps
                current_moment = datetime.datetime.now()
                time_string = current_moment.strftime("%m %d, %Y")
                unix_timestamp = int(time.time())
                
                # Construct fabricated record
                fabricated_review = {
                    "ReviewID": fabricated_review_id,
                    "reviewerID": fabricated_reviewer,
                    "asin": fabricated_asin,
                    "overall": random.uniform(1.0, 5.0),
                    "vote": "",
                    "verified": False,
                    "reviewTime": time_string,
                    "reviewerName": "",
                    "reviewText": "",
                    "summary": "",
                    "unixReviewTime": unix_timestamp,
                    "style": {}
                }
                tampered_dataset.append(fabricated_review)
                
            elif scenario_type == "--delete":
                if tampered_dataset:
                    tampered_dataset.pop()
                    
            elif scenario_type == "--modify":
                if tampered_dataset:
                    target_review = random.choice(tampered_dataset)
                    target_review['overall'] = random.uniform(1.0, 5.0)

            # Rebuild tree and measure time
            print(f"\nReconstructing tree after {scenario_type}...")
            
            tampered_tree = IntegrityTreeStructure()
            rebuild_start = time.time()
            tampered_apex, _ = tampered_tree.build_complete_tree(tampered_dataset)
            rebuild_end = time.time()
            
            timing_data.append(rebuild_end - rebuild_start)
            
            # Check for tampering detection
            if tampered_apex != baseline_apex:
                successful_detections += 1
                print("\nTampering DETECTED")
            
            total_simulations += 1
            print(f"===============================================================")
            scenario_iteration += 1
    
    # Calculate overall metrics
    detection_accuracy = successful_detections / total_simulations * 100 if total_simulations > 0 else 0
    average_detection_time = sum(timing_data) / len(timing_data) if timing_data else 0

    # Test root consistency
    consistency_tree = IntegrityTreeStructure()
    consistency_apex, _ = consistency_tree.build_complete_tree(record_data)
    consistency_status = "Stable" if consistency_apex == baseline_apex else "Unstable"

    # Display results
    print(f"\nTampering Detection Accuracy: {detection_accuracy:.1f}%")
    print(f"Average Detection Time: {average_detection_time:.3f} seconds")
    print(f"Apex Consistency: {consistency_status}")
    
    process_monitor = psutil.Process()
    memory_usage_mb = process_monitor.memory_info().rss / 1024 / 1024
    print(f"Memory Usage: {memory_usage_mb:.2f} MB")


def execute_performance_analysis(parameters):
    """
    Main entry point for performance analysis module
    
    Supports multiple benchmark modes:
    - --p N: Proof generation benchmarks (N iterations)
    - --s: Static metrics (construction time, memory)
    - --t: Tampering detection benchmarks
    - --all: Complete benchmark suite
    
    Args:
        parameters: Command-line arguments specifying benchmark mode
    """
    print("=== Performance Analysis Module ===")

    # Execute all benchmarks
    if not parameters or parameters[0] == '--all':
        proof_iterations = 1000 if not parameters or parameters[0] == '--all' else int(parameters[1]) if len(parameters) > 1 else 1000
        
        print(f"\nExecuting Complete Benchmark Suite (N={proof_iterations} for proofs)...")
        
        record_data, verification_tree, baseline_apex, build_duration, memory_peak = initialize_dataset_and_tree()
        if not record_data:
            return
        
        # Proof Generation Benchmark
        print("\n--- Proof Generation Benchmark ---")
        avg_proof_time, requirement_met, memory_used = execute_proof_benchmarks(record_data, verification_tree, proof_iterations)
        
        if avg_proof_time is not None:
            status_symbol = "✓" if "Met" in requirement_met else "✗"
            print("Authentication Proof Performance Benchmark")
            print(f"Sample Size: {proof_iterations} random reviews")
            print(f"Average Time: {avg_proof_time:.3f} ms {status_symbol} (< 100 ms requirement)")
            print(f"Memory Usage: {memory_used:.2f} MB")

        # Static Metrics Benchmark
        print("\n--- Static Metrics Benchmark ---")
        execute_static_benchmarks(record_data, verification_tree, build_duration, memory_peak)

        # Tampering Detection Benchmark
        print("\n--- Tampering Detection Benchmark ---")
        execute_tampering_benchmarks(record_data, verification_tree, baseline_apex)
        return

    # Proof-only benchmark
    if parameters[0] == '--p':
        if len(parameters) != 2:
            print("Usage: analyze-performance --p [N]")
            return
        
        try:
            proof_iterations = int(parameters[1])
            if proof_iterations < 1:
                print("N must be at least 1")
                return
        except ValueError:
            print("N must be integer value")
            return
        
        print(f"\nExecuting Proof Generation Benchmark (N={proof_iterations})...")
        
        record_data, verification_tree, baseline_apex, _, _ = initialize_dataset_and_tree()
        if not record_data:
            return
        
        avg_proof_time, requirement_met, memory_used = execute_proof_benchmarks(record_data, verification_tree, proof_iterations)

        if avg_proof_time is not None:
            status_symbol = "✓" if "Met" in requirement_met else "✗"
            print("Authentication Proof Performance Benchmark")
            print(f"Sample Size: {proof_iterations} random reviews")
            print(f"Average Time: {avg_proof_time:.3f} ms {status_symbol} (< 100 ms requirement)")
            print(f"Memory Usage: {memory_used:.2f} MB")
        return

    # Static-only benchmark
    if parameters[0] == '--s':
        print(f"\nExecuting Static Metrics Benchmark...")
        
        record_data, verification_tree, baseline_apex, build_duration, memory_peak = initialize_dataset_and_tree()
        if not record_data:
            return
        
        execute_static_benchmarks(record_data, verification_tree, build_duration, memory_peak)
        return

    # Tampering-only benchmark
    if parameters[0] == '--t':
        print(f"\nExecuting Tampering Detection Benchmark...")
        
        record_data, verification_tree, baseline_apex, _, _ = initialize_dataset_and_tree()
        if not record_data:
            return
        
        execute_tampering_benchmarks(record_data, verification_tree, baseline_apex)
        return

    print("Invalid option. Valid options: --p N, --s, --t, or --all")
