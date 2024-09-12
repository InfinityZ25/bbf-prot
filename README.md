# Bank Balance Forward (BBF) Demo

This project demonstrates a Bank Balance Forward operation implemented using MongoDB aggregation pipelines. It includes performance testing and visualization tools to analyze the efficiency of the operation across various dataset sizes.

## Overview

The Bank Balance Forward operation processes financial transactions, compressing older data and archiving transactions based on a specified time threshold. This implementation uses MongoDB for data storage and processing, leveraging its powerful aggregation framework.

## Features

- Seed database with sample transaction data
- Perform Bank Balance Forward operation
- Compress and archive old transactions
- Performance testing across different dataset sizes
- Visualization of execution times and document processing results

## Performance Results

![Bank Balance Forward Performance Chart](assets/demo_results.png)

The chart above illustrates the performance characteristics of the Bank Balance Forward operation:

- **Execution Time**: The top graph shows how execution time scales with the number of documents processed. The operation demonstrates non-linear growth but maintains efficiency even at large scales (1 million documents processed in about 34 seconds).

- **Document Processing**: The bottom graph breaks down the results of the operation, showing the number of compressed, archived, and remaining documents for each dataset size.

Key observations:
1. The operation scales well, handling 1 million documents in just over 34 seconds.
2. The majority of documents are archived, with the proportion remaining consistent across dataset sizes.
3. The number of compressed documents remains low, indicating effective compression.
4. There's a small increase in remaining documents as the dataset grows, but it stays a small fraction of the total.

## Getting Started

### Prerequisites

- Python 3.8+
- MongoDB
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/bbf-demo.git
   cd bbf-demo
   ```

2. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Ensure MongoDB is running on your local machine or update the connection string in the code if using a remote instance.

### Running the Demo

1. To run the main demo:
   ```
   python src/bbf_demo.py
   ```

2. To run performance tests and generate charts:
   ```
   python src/test_bank_balance_forward.py
   ```

3. For interactive experimentation, use the Jupyter notebook:
   ```
   jupyter notebook bank_balance_forward_demo.ipynb
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.