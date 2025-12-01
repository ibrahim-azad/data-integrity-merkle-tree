import json
import os
import datetime
import time

def display_progress_bar(label, percentage, time_display):
    filled_section = '#' * (percentage // 10)
    empty_section = '-' * (10 - len(filled_section))
    print(f"{label}: [{filled_section}{empty_section}] [{percentage:3}%] {time_display}", end='\r')

def convert_to_time_string(seconds_elapsed):
    minutes = int(seconds_elapsed // 60)
    seconds = int(seconds_elapsed % 60)
    return f"{minutes:02}:{seconds:02}"

class ReviewDataImporter:
    def __init__(self, dataset_identifier: str):
        self.dataset_identifier = dataset_identifier
        self.raw_data_directory = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
        self.source_file_path = os.path.join(self.raw_data_directory, f'{dataset_identifier}.json')
        self.imported_records = []

    def request_record_count(self, maximum_records=1500000):
        while True:
            try:
                count = int(input(f"Specify number of records to import (max {maximum_records}): "))
                if 1 <= count <= maximum_records:
                    return count
                else:
                    print(f"Value must be between 1 and {maximum_records}.")
            except ValueError:
                print("Invalid input. Integer required.")

    def load_and_process(self, record_count=None):
        if not os.path.exists(self.source_file_path):
            raise FileNotFoundError(f"Dataset file not found: {self.source_file_path}")
        if record_count is None:
            record_count = self.request_record_count()
        self.imported_records = []
        import_start = time.time()
        print()
        with open(self.source_file_path, 'r', encoding='utf-8') as source_file:
            for line_number, json_line in enumerate(source_file):
                if line_number >= record_count:
                    break
                record = json.loads(json_line)
                self.imported_records.append(record)
                if line_number % (record_count // 10) == 0 or line_number == record_count - 1:
                    progress_percent = int((line_number + 1) / record_count * 100)
                    display_progress_bar("Importing Records", progress_percent, convert_to_time_string(time.time() - import_start))
        self.imported_records, self.statistics = self.sanitize_and_normalize(self.imported_records)
        return self.imported_records, self.statistics

    def persist_processed_data(self):
        output_directory = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
        os.makedirs(output_directory, exist_ok=True)
        output_file_path = os.path.join(output_directory, f'{self.dataset_identifier}_proc.json')
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            json.dump(self.imported_records, output_file, separators=(',', ':'), ensure_ascii=False)

    def sanitize_and_normalize(self, raw_records):
        # Define default values for missing fields
        field_defaults = {
            "overall": 0.0,
            "vote": "",
            "verified": False,
            "reviewTime": "",
            "reviewerID": "",
            "asin": "",
            "style": {},
            "reviewerName": "",
            "reviewText": "",
            "summary": "",
            "unixReviewTime": 0
        }
        text_field_list = ["vote", "reviewTime", "reviewerID", "asin", "reviewerName", "reviewText", "summary"]
        
        initial_count = len(raw_records)
        fields_corrected = 0
        duplicate_tracker = set()
        deduplicated_records = []
        
        processing_start = time.time()
        print()
        record_total = len(raw_records)
        
        for index, record in enumerate(raw_records):
            # Fill missing fields with defaults
            for field_key, default_value in field_defaults.items():
                if field_key not in record:
                    record[field_key] = default_value
                    fields_corrected += 1
            
            # Normalize text encoding
            for text_field in text_field_list:
                if isinstance(record[text_field], str):
                    record[text_field] = record[text_field].encode('utf-8').decode('utf-8').strip()
            
            # Type validation and conversion
            try:
                record["overall"] = float(record["overall"])
            except (ValueError, TypeError):
                record["overall"] = 0.0
            
            record["verified"] = bool(record["verified"])
            
            try:
                record["unixReviewTime"] = int(record["unixReviewTime"])
            except (ValueError, TypeError):
                record["unixReviewTime"] = 0
            
            if not isinstance(record["style"], dict):
                record["style"] = {}
            
            # Deduplication based on composite key
            composite_key = (record["reviewerID"], record["asin"], record["unixReviewTime"])
            if composite_key not in duplicate_tracker:
                duplicate_tracker.add(composite_key)
                deduplicated_records.append(record)
            
            if index % (record_total // 10) == 0 or index == record_total - 1:
                progress_percent = int((index + 1) / record_total * 100)
                display_progress_bar("Sanitizing Data", progress_percent, convert_to_time_string(time.time() - processing_start))
        print()
        
        # Generate unique identifiers
        id_generation_start = time.time()
        unique_record_count = len(deduplicated_records)
        for index, record in enumerate(deduplicated_records):
            record["ReviewID"] = f"R{index:06d}"
            if index % (unique_record_count // 10) == 0 or index == unique_record_count - 1:
                progress_percent = int((index + 1) / unique_record_count * 100)
                display_progress_bar("Assigning IDs", progress_percent, convert_to_time_string(time.time() - id_generation_start))
        print()
        
        print("\nPersisting processed records...")
        save_start = time.time()
        self.imported_records = deduplicated_records
        self.persist_processed_data()
        save_elapsed = time.time() - save_start
        print(f"✓ Processed data persisted. Duration: {save_elapsed:.2f} seconds")

        processing_statistics = {
            "total_loaded": initial_count,
            "valid_records": len(deduplicated_records),
            "duplicates_removed": initial_count - len(deduplicated_records),
            "missing_fields_handled": fields_corrected,
            "unique_ids_generated": len(deduplicated_records),
            "save_time": save_elapsed
        }
        return deduplicated_records, processing_statistics

    def retrieve_records(self):
        return self.imported_records

    def retrieve_statistics(self):
        return self.statistics