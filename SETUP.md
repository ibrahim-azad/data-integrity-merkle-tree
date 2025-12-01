# Setup and Installation Guide

Complete guide to setting up and running the Data Integrity Verification System.

## Prerequisites

- **Python 3.8+** installed
- **pip** package manager
- **Git** (for cloning repository)
- At least **2GB RAM** (for processing large datasets)
- **500MB disk space** (for dataset and processed files)

## Step-by-Step Installation

### 1. Clone or Download Repository

**Option A: Using Git**
```bash
git clone https://github.com/ibrahim-azad/data-integrity-merkle-tree.git
cd data-integrity-merkle-tree
```

**Option B: Download ZIP**
- Download and extract the ZIP file
- Open terminal/command prompt in the extracted folder

### 2. Create Project Structure

Create required directories:

```bash
mkdir -p data/raw
mkdir -p data/processed
mkdir -p roots
mkdir -p src
```

**On Windows:**
```cmd
mkdir data\raw
mkdir data\processed
mkdir roots
mkdir src
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

**Note:** The `--break-system-packages` flag is needed for some Python installations.

If that doesn't work, try:
```bash
pip install psutil
```

### 4. Organize Your Files

Move all `.py` files into the `src/` directory:

```
data-integrity-merkle-tree/
├── src/
│   ├── command_interface.py
│   ├── crypto_hash_tree.py
│   ├── dataset_processor.py
│   ├── dataset_modifier.py
│   ├── integrity_checker.py
│   ├── proof_generator.py
│   ├── anomaly_detector.py
│   ├── performance_analyzer.py
│   └── validation_suite.py
├── data/
│   ├── raw/
│   └── processed/
├── roots/
├── README.md
├── requirements.txt
└── .gitignore
```

### 5. Download Dataset

**Amazon Electronics Reviews Dataset:**

1. Visit: http://jmcauley.ucsd.edu/data/amazon/
2. Download "Electronics" category (5-core reviews)
3. Save as `data/raw/electronics.json`

**Alternative: Create Test Dataset**

If you don't have the actual dataset, create a small test file:

```bash
cd data/raw
```

Create `electronics.json` with sample data (copy this into the file):

```json
{"reviewerID": "A2SUAM1J3GNN3B", "asin": "0000013714", "reviewerName": "J. McDonald", "helpful": [2, 3], "reviewText": "Great product!", "overall": 5.0, "summary": "Loved it", "unixReviewTime": 1400630400, "reviewTime": "05 21, 2014"}
{"reviewerID": "A3VTQ6J5J5WXQ1", "asin": "0000013714", "reviewerName": "Peter", "helpful": [0, 0], "reviewText": "Not bad", "overall": 4.0, "summary": "Good", "unixReviewTime": 1388361600, "reviewTime": "12 30, 2013"}
```

(Add more lines for larger test datasets)

### 6. Verify Installation

Test that everything is set up correctly:

```bash
cd src
python command_interface.py
```

You should see:
```
Data Integrity Verification System - Command Interface
Enter 'commands' for available operations or 'quit' to exit.

$
```

Type `commands` to see available operations.

## First Run Tutorial

### Import and Process Data

```bash
$ import-data electronics 1000
```

This will:
- Load 1,000 reviews from the dataset
- Remove duplicates
- Sanitize data
- Assign unique ReviewIDs
- Save processed data to `data/processed/`

### Build the Merkle Tree

```bash
$ construct-tree electronics
```

This will:
- Create hash tree from processed data
- Compute root hash
- Save root hash to `roots/` directory
- Display tree statistics

### Verify Integrity

```bash
$ check-integrity electronics
```

Compares current data against stored root hash.

### Generate Authentication Proof

```bash
$ locate electronics R000000
```

Generates Merkle proof for the first record.

### Test Tampering Detection

```bash
$ detect-tampering electronics --modify 3
```

Simulates 3 modification attacks and validates detection.

## Common Issues and Solutions

### Issue: "Module not found: psutil"

**Solution:**
```bash
pip install psutil
```

### Issue: "Dataset file not found"

**Solution:**
- Verify `electronics.json` is in `data/raw/` directory
- Check file name spelling (case-sensitive on Linux/Mac)

### Issue: "Permission denied" when running

**Solution (Linux/Mac):**
```bash
chmod +x src/command_interface.py
```

### Issue: "Processed dataset not found"

**Solution:**
- Run `import-data` command first before other commands
- Verify `data/processed/` directory exists

### Issue: Unicode/encoding errors (✓ ✗ showing as â)

**Solution:**
- This is a terminal encoding issue
- On Windows: Use Windows Terminal or set terminal encoding to UTF-8
- The system still works correctly

## Performance Tips

### For Large Datasets (100K+ records)

1. **Increase available RAM:** Close other applications
2. **Use SSD storage:** Faster I/O for large files
3. **Start small:** Test with 10K records before scaling up

### Recommended Dataset Sizes

- **Testing:** 1,000 - 10,000 records
- **Development:** 50,000 - 100,000 records
- **Benchmarking:** 1,000,000 records

### Memory Usage Estimates

- 10K records: ~50 MB
- 100K records: ~200 MB
- 1M records: ~450 MB

## Running Tests

Execute the test suite:

```bash
$ run-tests --all
```

Or run individual tests:
```bash
$ run-tests 1    # Import test
$ run-tests 2    # Tree construction
$ run-tests 5    # Tampering detection
```

## Advanced Usage

### Custom Dataset

To use your own dataset:

1. Format as JSONL (one JSON object per line)
2. Include required fields: `reviewerID`, `asin`, `overall`
3. Place in `data/raw/[your-dataset].json`
4. Import using: `import-data [your-dataset] [N]`

### Batch Operations

Process multiple datasets:
```bash
$ import-data dataset1 10000
$ construct-tree dataset1
$ import-data dataset2 20000
$ construct-tree dataset2
```

### Performance Analysis

Run comprehensive benchmarks:
```bash
$ analyze-performance --all
```

Options:
- `--p N`: Authentication proofs (N iterations)
- `--s`: Static metrics
- `--t`: Tampering detection
- `--all`: Complete suite

## Troubleshooting

### Debug Mode

Add print statements in the code to debug:
```python
print(f"DEBUG: {variable_name}")
```

### Check File Paths

Verify all directories exist:
```bash
ls -la data/raw
ls -la data/processed
ls -la roots
```

### Reset Everything

To start fresh:
```bash
rm -rf data/processed/*
rm -rf roots/*
```

Then re-import data.

## Getting Help

- Check `README.md` for feature documentation
- Type `commands` in CLI for available operations
- Review error messages carefully - they usually indicate the problem

## Next Steps

After successful setup:

1. Import a small dataset (1K records)
2. Build the tree
3. Try modifying data
4. Verify integrity detection
5. Generate authentication proofs
6. Run performance benchmarks

Explore different commands and experiment with the system!

## Contact

For questions or issues:
- Muhammad Ibrahim Azad
- Email: ibrahimazad1590@gmail.com
- GitHub: github.com/ibrahim-azad
