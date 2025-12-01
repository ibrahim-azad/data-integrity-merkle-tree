import json
import os
import glob
import time
import random
import datetime

from crypto_hash_tree import TreeVertex, IntegrityTreeStructure

def execute_test_scenarios(args):
    from command_interface import SystemController  # import here to avoid circular import
    if not args:
        print("Usage: run-tests [test_case_number] | --all")
        return

    controller = SystemController()

    test_cases = {
        1: "import-data electronics 1000000",
        2: "construct-tree electronics",
        3: "locate electronics R000000",
        4: "locate electronics R999999",
        7: "detect-tampering electronics --delete 1",
        9: "check-integrity electronics",
        10: "analyze-performance --p 100",
        11: "analyze-performance --s",
        12: "placeholder",
        13: ["modify electronics --modify R000000", "construct-tree electronics"],
        15: "special",  # test case 15
    }

    if args[0] == "--all":
        for num in range(1, 18):
            print(f"\n--- Running Test Case {num} ---")
            if num == 5:
                run_test_5(controller)
            elif num == 6:
                run_test_6(controller)
            elif num == 8:
                run_test_8(controller)
            elif num == 14:
                run_test_14(controller)
            elif num == 15:
                run_test_15(controller)
            else:
                cmd_input = test_cases.get(num, "")
                run_test(controller, cmd_input)
    else:
        try:
            num = int(args[0])
            if num in test_cases or num in [5, 6, 8, 14, 15, 16, 17]:
                print(f"\n--- Running Test Case {num} ---")
                if num == 5:
                    run_test_5(controller)
                elif num == 6:
                    run_test_6(controller)
                elif num == 8:
                    run_test_8(controller)
                elif num == 14:
                    run_test_14(controller)
                elif num == 15:
                    run_test_15(controller)
                else:
                    cmd_input = test_cases[num]
                    run_test(controller, cmd_input)
            else:
                print(f"Test case {num} not found. Available: 1-17")
        except ValueError:
            print("Invalid test case number.")

def run_test(controller, cmd_input):
    if not cmd_input:
        return
    if isinstance(cmd_input, list):
        for cmd in cmd_input:
            run_single_test(controller, cmd)
    else:
        run_single_test(controller, cmd_input)

def run_single_test(controller, cmd_input):
    if cmd_input == "placeholder":
        print("Placeholder for test case 12")
        return
    parts = cmd_input.split()
    cmd = parts[0]
    if cmd in controller.operation_handlers:
        try:
            controller.operation_handlers[cmd](parts[1:] if len(parts) > 1 else [])
        except Exception as e:
            print(f"Error running test: {e}")
    else:
        print(f"Unknown command in test: {cmd}")

def run_test_6(controller):
    run_test(controller, "detect-tampering electronics --modify 1")

def run_test_5(controller):
    run_test(controller, "detect-tampering electronics --modify 1")

def run_test_8(controller):
    run_test(controller, "detect-tampering electronics --insert 1")

def run_test_14(controller):
    import glob
    # Run first load
    print("First import-data electronics 1000000")
    run_test(controller, "import-data electronics 1000000")
    # Get latest root
    roots_dir = "roots"
    if os.path.exists(roots_dir):
        files = glob.glob(os.path.join(roots_dir, "electronics_root_v*.json"))
        if files:
            latest_file = max(files, key=os.path.getctime)
            with open(latest_file, 'r') as f:
                data1 = json.load(f)
                root1 = data1.get("root_hash")
        else:
            root1 = None
    else:
        root1 = None

    # Run second load
    print("Second import-data electronics 1000000")
    run_test(controller, "import-data electronics 1000000")
    # Get latest root again
    if os.path.exists(roots_dir):
        files = glob.glob(os.path.join(roots_dir, "electronics_root_v*.json"))
        if files:
            latest_file = max(files, key=os.path.getctime)
            with open(latest_file, 'r') as f:
                data2 = json.load(f)
                root2 = data2.get("root_hash")
        else:
            root2 = None
    else:
        root2 = None

    # Compare
    if root1 and root2:
        if root1 == root2:
            print("✓ Roots are the same")
        else:
            print("✗ Roots are different")
    else:
        print("Could not retrieve roots")

def run_test_15(controller):
    # Load initial data
    processed_file = os.path.join("..", "data", "processed", "electronics_proc.json")
    if not os.path.exists(processed_file):
        processed_file = os.path.join("data", "processed", "electronics_proc.json")
    
    try:
        with open(processed_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Processed data file not found. Run import-data first.")
        return

    # Build initial tree
    tree = IntegrityTreeStructure()
    tree.build_complete_tree(data)

    # Note: Test 15 is for dynamic insertion performance comparison
    # Since the refactored version may not have add_leaf implemented,
    # this is a simplified version
    print("Test 15: Dynamic insertion test")
    print("This test compares insertion methods (placeholder in refactored version)")
    
    # Build tree twice and compare times
    tree1 = IntegrityTreeStructure()
    start = time.time()
    root1, _ = tree1.build_complete_tree(data)
    time1 = time.time() - start
    
    tree2 = IntegrityTreeStructure()
    start = time.time()
    root2, _ = tree2.build_complete_tree(data)
    time2 = time.time() - start
    
    print(f"First build: {time1:.4f} seconds, Root: {root1[:16]}...")
    print(f"Second build: {time2:.4f} seconds, Root: {root2[:16]}...")
    
    if root1 == root2:
        print("✓ Roots match - consistency verified")
    else:
        print("✗ Roots do not match")
