# Bank Balance Forward

This project implements a Bank Balance Forward process for compressing and archiving transaction data in MongoDB. It's designed to handle large volumes of financial transactions efficiently.

## Features

- Compresses transactions for each client into summary records
- Archives old transactions
- Handles large datasets (tested up to 1 million records)
- Includes comprehensive test suite

## Requirements

- Python 3.7+
- MongoDB
- PyMongo
- Matplotlib (for test result visualization)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/bank-balance-forward.git
   cd bank-balance-forward
   ```

2. Install the required packages:
   ```
   pip install pymongo matplotlib
   ```

3. Ensure you have MongoDB running locally on the default port (27017).

## Usage

The main functionality is provided by the `bank_balance_forward` function. Here's a basic usage example:

```python
from bank_balance_forward import bank_balance_forward

result = bank_balance_forward(days_threshold=30)
print(f"Compressed {result['compressed_count']} transactions")
print(f"Archived {result['archived_count']} transactions")
print(f"Remaining transactions: {result['remaining_count']}")
```

## Configuration

You can adjust the following parameters in the `bank_balance_forward` function:

- `days_threshold`: The number of days back from which to start compressing transactions

## Testing

To run the test suite:

```
python -m unittest test_bank_balance_forward.py
```

This will run a series of tests with different dataset sizes and generate a performance chart saved as `bank_balance_forward_performance.png`.

## Performance

The performance of the Bank Balance Forward process has been tested with datasets ranging from 1,000 to 1,000,000 records. Refer to the generated performance chart for detailed metrics.

## Structure

- `bank_balance_forward.py`: Main script containing the core functionality
- `test_bank_balance_forward.py`: Test suite and performance testing script

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.