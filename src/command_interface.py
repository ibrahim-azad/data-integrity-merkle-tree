import sys
from dataset_processor import ReviewDataImporter
import time
import json
import os
import datetime
from crypto_hash_tree import IntegrityTreeStructure
from dataset_modifier import perform_dataset_update
from integrity_checker import execute_integrity_check
from proof_generator import locate_and_verify_record
from anomaly_detector import run_tampering_detection
from performance_analyzer import execute_performance_analysis
from validation_suite import execute_test_scenarios

class SystemController:
    def __init__(self):
        self.operation_handlers = {
            "import-data": self.import_dataset,
            "construct-tree": self.construct_verification_tree,
            "modify": perform_dataset_update,
            "check-integrity": execute_integrity_check,
            "locate": locate_and_verify_record,
            "detect-tampering": run_tampering_detection,
            "analyze-performance": execute_performance_analysis,
            "run-tests": execute_test_scenarios,
            "cls": self.clear_display,
            "quit": self.terminate_interface,
            "commands": self.display_commands
        }

    def start(self):
        print("Data Integrity Verification System - Command Interface")
        print("Enter 'commands' for available operations or 'quit' to exit.")
        while True:
            try:
                user_input = input("\n$ ").strip()
                if not user_input:
                    continue
                input_parts = user_input.split()
                operation = input_parts[0]
                if operation in self.operation_handlers:
                    self.operation_handlers[operation](input_parts[1:] if len(input_parts) > 1 else [])
                else:
                    print("Unknown operation. Enter 'commands' for available operations.")
            except KeyboardInterrupt:
                print("\nTerminating interface.")
                break
            except Exception as error:
                print(f"Error occurred: {error}")

    def import_dataset(self, parameters):
        if len(parameters) != 2:
            print("Usage: import-data [DatasetName] [RecordCount]")
            return
        dataset_identifier = parameters[0]
        try:
            record_limit = int(parameters[1])
            if record_limit < 1 or record_limit > 1500000:
                print("Record count must be within range 1-1,500,000.")
                return
        except ValueError:
            print("Invalid record count. Must be integer value.")
            return

        importer = ReviewDataImporter(dataset_identifier)
        operation_start = time.time()
        try:
            records, processing_stats = importer.load_and_process(record_limit)
            operation_end = time.time()
            total_time = operation_end - operation_start
            if records:
                print(f"\n✓ Import successful: {processing_stats['total_loaded']:,} records")
                print(f"✓ Valid entries: {processing_stats['valid_records']:,}")
                print(f"✓ Duplicates filtered: {processing_stats['duplicates_removed']:,}")
                print(f"✓ Missing data handled: {processing_stats['missing_fields_handled']:,}")
                print(f"✓ Unique identifiers assigned: {processing_stats['unique_ids_generated']:,}")
                print(f"✓ Processing time: {total_time - processing_stats['save_time']:.2f} seconds")
            else:
                print("No records imported.")
        except FileNotFoundError as error:
            print(f"Error: {error}")
        except Exception as error:
            print(f"Import error: {error}")

    def construct_verification_tree(self, parameters):
        if len(parameters) != 1:
            print("Usage: construct-tree [ProcessedDatasetName]")
            return
        dataset_name = parameters[0]
        processed_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', f'{dataset_name}_proc.json')
        if not os.path.exists(processed_path):
            print(f"Processed dataset not located: {processed_path}")
            return
        try:
            with open(processed_path, 'r', encoding='utf-8') as file_handle:
                record_set = json.load(file_handle)
        except Exception as error:
            print(f"Error reading processed data: {error}")
            return

        hash_tree = IntegrityTreeStructure()
        construction_start = time.time()
        apex_hash, memory_consumed = hash_tree.build_complete_tree(record_set)
        construction_duration = time.time() - construction_start

        if not apex_hash:
            print("Tree construction failed.")
            return

        leaf_count = len(hash_tree.terminal_list)
        structure_height = self.compute_tree_height(hash_tree.apex_vertex)
        vertex_total = self.compute_vertex_count(hash_tree.apex_vertex)

        print("\nTree Construction Results:")
        print(f"- Terminal vertices (leaves): {leaf_count:,}")
        print(f"- Structure height: {structure_height}")
        print(f"- Total vertices: {vertex_total:,}")
        print(f"- Apex Hash (Root): {apex_hash}")

        storage_directory = os.path.join(os.path.dirname(__file__), 'roots')
        os.makedirs(storage_directory, exist_ok=True)
        version_number = self.determine_next_version(storage_directory, dataset_name)
        root_storage_file = os.path.join(storage_directory, f'{dataset_name}_root_v{version_number:.1f}.json')

        save_operation_start = time.time()
        apex_metadata = {
            "timestamp": datetime.datetime.now().isoformat(),
            "root_hash": apex_hash,
            "record_count": leaf_count,
            "dataset": dataset_name,
            "tree_height": structure_height
        }
        with open(root_storage_file, 'w', encoding='utf-8') as file_handle:
            json.dump(apex_metadata, file_handle, indent=4)
        save_operation_duration = time.time() - save_operation_start

        print("\nPersisting apex hash...")
        print(f"✓ Apex saved to: {root_storage_file}")
        print("\nStored Metadata:")
        print(json.dumps(apex_metadata, indent=4))
        print(f"\nConstruction time: {construction_duration:.2f} seconds")
        print(f"Storage time: {save_operation_duration * 1000:.2f} ms")

    def determine_next_version(self, directory_path, dataset_identifier):
        directory_contents = os.listdir(directory_path)
        version_list = []
        filename_prefix = f'{dataset_identifier}_root_v'
        for filename in directory_contents:
            if filename.startswith(filename_prefix) and filename.endswith('.json'):
                try:
                    version_string = filename[len(filename_prefix):-5]  # Strip .json
                    version_value = float(version_string)
                    version_list.append(version_value)
                except ValueError:
                    pass
        if not version_list:
            return 1.0
        return max(version_list) + 0.1

    def compute_tree_height(self, vertex):
        if not vertex:
            return 0
        left_height = self.compute_tree_height(vertex.left_child)
        right_height = self.compute_tree_height(vertex.right_child)
        return 1 + max(left_height, right_height)

    def compute_vertex_count(self, vertex):
        if not vertex:
            return 0
        left_count = self.compute_vertex_count(vertex.left_child)
        right_count = self.compute_vertex_count(vertex.right_child)
        return 1 + left_count + right_count

    def clear_display(self, parameters):
        os.system('cls' if os.name == 'nt' else 'clear')

    def terminate_interface(self, parameters):
        print("Terminating command interface.")
        sys.exit(0)

    def display_commands(self, parameters):
        print("Available Operations:\n")
        print("import-data [dataset_name] [N]")
        print("Import and process specified dataset with N records")
        print()
        print("construct-tree [dataset_name]")
        print("Build hash tree structure from processed dataset")
        print()
        print("modify [dataset_name] [action] [reviewID]")
        print("Modify processed dataset (reviewID optional for --insert)")
        print()
        print("check-integrity [dataset_name]")
        print("Verify data integrity via apex hash comparison")
        print()
        print("locate [dataset_name] [reviewID]")
        print("Generate and validate authentication path for record")
        print()
        print("detect-tampering [dataset_name] [action] [N]")
        print("Execute tampering detection simulation")
        print()
        print("analyze-performance [--p N | --s | --t | --all]")
        print("Execute performance benchmarks:")
        print("  --p N: Authentication path benchmarks (N iterations)")
        print("  --s: Static verification benchmarks")
        print("  --t: Tampering detection benchmarks")
        print("  --all: Complete benchmark suite")
        print()
        print("run-tests [test_number] | --all")
        print("Execute specific test scenario or complete test suite")
        print()
        print("cls")
        print("Clear terminal display")
        print()
        print("commands")
        print("Display this command reference")
        print()
        print("quit")
        print("Exit command interface")

if __name__ == "__main__":
    controller = SystemController()
    controller.start()
