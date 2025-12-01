# Data Integrity Verification System

A cryptographic data integrity system using **Merkle Trees** (Binary Hash Trees) to detect tampering in large-scale datasets. Built for verifying authenticity of 1M+ Amazon product reviews using SHA-256 hashing and authentication proofs.

## Overview

This system implements a **Merkle Tree** - the same cryptographic data structure used in:
- Bitcoin and blockchain systems
- Git version control
- IPFS distributed storage
- Certificate transparency logs

The project processes Amazon review datasets, constructs tamper-evident hash trees, and provides efficient verification mechanisms to detect any unauthorized data modifications.

## Key Features

### Data Integrity Verification
- SHA-256 cryptographic hashing for tamper detection
- Root hash comparison for instant integrity verification
- Detects insertions, modifications, and deletions in O(n) time

### Authentication Proofs
- Generate Merkle proofs for individual records
- Verify record existence with O(log n) hash operations
- Authentication path validation against root hash

### Performance Optimization
- Smart batch processing (incremental vs. rebuild strategy)
- Path-only updates: O(log n) vs. O(n) full rebuild
- Handles 1,000,000+ records efficiently
- Memory usage tracking and optimization

### Tampering Detection
- Simulates real-world attack scenarios
- Tests against insertion, modification, and deletion attacks
- Comprehensive detection benchmarking

### Command-Line Interface
- Interactive CLI for all operations
- Dataset import and preprocessing
- Tree construction and verification
- Performance analysis tools

## Architecture

### Merkle Tree Structure

```
                    Root Hash (Apex)
                   /                \
            H(AB)                      H(CD)
           /     \                    /     \
       H(A)     H(B)              H(C)     H(D)
        |        |                 |        |
      Data A   Data B            Data C   Data D
```

Each parent hash is computed from its children:
- `H(AB) = SHA256(H(A) + H(B))`
- Root hash represents entire dataset integrity
- Any data change propagates up to root

### System Components

**Core Modules:**
- `crypto_hash_tree.py` - Merkle tree implementation
- `dataset_processor.py` - Data import and sanitization
- `command_interface.py` - CLI controller

**Verification Modules:**
- `integrity_checker.py` - Dataset integrity validation
- `proof_generator.py` - Authentication path generation
- `anomaly_detector.py` - Tampering detection simulation

**Analysis Modules:**
- `performance_analyzer.py` - Benchmarking suite
- `validation_suite.py` - Automated test scenarios

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ibrahim-azad/data-integrity-merkle-tree.git
cd data-integrity-merkle-tree
```

2. Install dependencies:
```bash
pip install -r requirements.txt --break-system-packages
```

3. Download dataset:
- Download Amazon Reviews dataset (Electronics)
- Place in `data/raw/electronics.json`
- Dataset format: One JSON object per line

## Usage

### Start the CLI

```bash
python src/command_interface.py
```

### Basic Operations

**1. Import Dataset**
```bash
$ import-data electronics 100000
```
Imports and processes 100,000 reviews with deduplication and sanitization.

**2. Build Merkle Tree**
```bash
$ construct-tree electronics
```
Constructs hash tree and stores root hash for integrity verification.

**3. Verify Integrity**
```bash
$ check-integrity electronics
```
Compares current dataset against stored root hash.

**4. Generate Authentication Proof**
```bash
$ locate electronics R000042
```
Creates and validates Merkle proof for specific record.

**5. Detect Tampering**
```bash
$ detect-tampering electronics --modify 5
```
Simulates 5 modification attacks and validates detection.

**6. Performance Analysis**
```bash
$ analyze-performance --all
```
Runs comprehensive benchmarking suite.

### Available Commands

```
import-data [dataset_name] [N]           - Import N records
construct-tree [dataset_name]            - Build hash tree
modify [dataset_name] [action] [id]      - Modify dataset
check-integrity [dataset_name]           - Verify integrity
locate [dataset_name] [reviewID]         - Generate proof
detect-tampering [dataset] [action] [N]  - Tampering simulation
analyze-performance [options]            - Run benchmarks
run-tests [test_number | --all]          - Execute tests
cls                                      - Clear screen
commands                                 - Show this help
quit                                     - Exit
```

## Performance Benchmarks

Tested on 1,000,000 Amazon review records:

### Authentication Proof Generation
- Average time: **2.847 ms** (< 100 ms requirement)
- Path length: O(log n) ≈ 20 hash operations
- Memory usage: ~450 MB for 1M records

### Tree Construction
- Per-record hash time: **0.0012 ms**
- Total construction: **18.5 seconds** for 1M records
- Peak memory: **425 MB**

### Tampering Detection
- Detection accuracy: **100%** across all scenarios
- Average detection time: **18.2 seconds** (full rebuild)
- Root consistency: **Stable** across repeated builds

## Technical Details

### Cryptographic Properties

**Hash Function:** SHA-256
- Collision resistance: 2^256 security
- Deterministic output
- Avalanche effect (1-bit change → 50% output change)

**Tree Properties:**
- Height: O(log n) for n records
- Total nodes: O(n)
- Proof size: O(log n) hashes

### Optimization Strategies

**Smart Batch Processing:**
- Small batches (< 50% tree size): Incremental addition
- Large batches (> 50% tree size): Full rebuild
- Automatic strategy selection

**Path-Only Updates:**
- Modification: Update O(log n) nodes vs O(n) rebuild
- Performance gain: **~342x faster** for single modifications

**Memory Management:**
- Streaming JSON parsing for large datasets
- Incremental processing with progress tracking
- Peak memory monitoring

## Project Structure

```
data-integrity-merkle-tree/
├── src/
│   ├── command_interface.py       # CLI controller
│   ├── crypto_hash_tree.py        # Merkle tree core
│   ├── dataset_processor.py       # Data import
│   ├── dataset_modifier.py        # Data modification
│   ├── integrity_checker.py       # Verification
│   ├── proof_generator.py         # Authentication paths
│   ├── anomaly_detector.py        # Tampering detection
│   ├── performance_analyzer.py    # Benchmarking
│   └── validation_suite.py        # Test automation
├── data/
│   ├── raw/                       # Original datasets
│   └── processed/                 # Sanitized data
├── roots/                         # Stored root hashes
├── README.md
├── requirements.txt
└── .gitignore
```

## Algorithm Complexity

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Tree Construction | O(n) | O(n) |
| Single Insert | O(n) | O(1) |
| Single Modify | O(log n) | O(1) |
| Batch Insert | O(n) or O(k) | O(k) |
| Generate Proof | O(log n) | O(log n) |
| Verify Proof | O(log n) | O(1) |
| Integrity Check | O(n) | O(n) |

Where:
- n = total records in tree
- k = number of records in batch

## Use Cases

**Supply Chain Verification:**
- Track product authenticity
- Detect counterfeit modifications
- Audit trail verification

**Database Integrity:**
- Detect unauthorized data changes
- Efficient integrity proofs
- Distributed database synchronization

**Audit Logging:**
- Tamper-evident log systems
- Compliance verification
- Forensic analysis

**Document Verification:**
- Certificate transparency
- Medical records integrity
- Legal document authentication

## Testing

Run automated test suite:

```bash
$ run-tests --all
```

Individual test scenarios:
```bash
$ run-tests 1    # Import test
$ run-tests 5    # Tampering detection
$ run-tests 14   # Root consistency
```

## Limitations

- Root hash storage: Currently file-based (could use database)
- Dataset size: Limited by available RAM for in-memory processing
- Single-threaded: No parallel hash computation (could optimize)
- CLI-only: No web interface or API

## Future Enhancements

- Persistent tree storage (database integration)
- Parallel hash computation using multiprocessing
- REST API for integration
- Web dashboard for visualization
- Incremental verification (check only changed subtrees)
- Support for multiple hash algorithms (SHA3, BLAKE2)

## Technical Background

### Why Merkle Trees?

**Efficiency:** Verify individual records without checking entire dataset
- Traditional approach: Hash entire dataset → O(n) always
- Merkle tree: Verify one record → O(log n) with proof

**Scalability:** Logarithmic proof size
- 1,000 records → ~10 hashes in proof
- 1,000,000 records → ~20 hashes in proof
- 1,000,000,000 records → ~30 hashes in proof

**Security:** Cryptographically secure
- Cannot forge valid proof without breaking SHA-256
- Any tampering detected immediately
- Pre-image resistance prevents reverse engineering

## Educational Value

This project demonstrates:
- Cryptographic hash functions and properties
- Binary tree data structures
- Algorithm optimization techniques
- Large-scale data processing
- Command-line interface design
- Software architecture patterns

Concepts covered:
- Merkle trees and authentication paths
- Cryptographic integrity verification
- Time and space complexity analysis
- Performance benchmarking
- Test-driven development

## License

MIT License - Feel free to use for educational purposes

## Author

Muhammad Ibrahim Azad  
Computer Science Student, FAST University Islamabad  
AI Intern @ NESCOM Pakistan

## Acknowledgments

- Dataset: Amazon Product Reviews (Electronics)
- Inspired by blockchain and Git internals
- Built as final project for Algorithms course

---

**Note:** This is an educational project demonstrating Merkle tree concepts. For production use, consider established libraries like `merkletools` or `pymerkle`.
