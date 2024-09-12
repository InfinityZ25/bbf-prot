"""
This module contains unit tests for the bank balance forward functionality.

It includes test cases to verify the performance of the bank_balance_forward
function with various dataset sizes, and generates a performance chart.
"""

import unittest
from datetime import UTC, datetime

import matplotlib.pyplot as plt
import numpy as np
from pymongo import MongoClient

from bbf_demo import bank_balance_forward, seed_database


class TestBankBalanceForward(unittest.TestCase):
    """
    Test case for the bank_balance_forward function performance.

    This class contains unit tests to measure and visualize the performance
    of the bank_balance_forward function with different dataset sizes.
    """

    @classmethod
    def setUpClass(cls):
        # Connect to the same database as in the demo
        cls.client = MongoClient('mongodb://localhost:27017')
        cls.db = cls.client['items']

    @classmethod
    def tearDownClass(cls):
        # Drop the database
        cls.client.drop_database('items')
        cls.client.close()

    def setUp(self):
        # Clear all collections before each test
        self.db.ledger_line_items.drop()
        self.db.compressed_transactions.drop()
        self.db.archived_items.drop()

    def run_test_and_measure(self, num_documents, compression_threshold, timeout=300):
        print(f"\\nTesting with {num_documents} documents...")
        seed_start = datetime.now(UTC)
        seed_database(num_documents=num_documents, batch_size=5000)
        seed_end = datetime.now(UTC)
        print(f"Seeding completed in {
              (seed_end - seed_start).total_seconds():.2f} seconds")

        start_time = datetime.now(UTC)
        result = bank_balance_forward(compression_threshold)
        end_time = datetime.now(UTC)
        execution_time = (end_time - start_time).total_seconds()

        if execution_time > timeout:
            print(f"Test case for {num_documents} documents timed out after {
                  timeout} seconds")
            return None

        return {
            'num_documents': num_documents,
            'execution_time': execution_time,
            'compressed_count': result['compressed_count'],
            'archived_count': result['archived_count'],
            'remaining_count': result['remaining_count']
        }

    def test_performance_chart(self):
        test_cases = [
            (1_000, 30),
            (10_000, 30),
            (50_000, 30), # Performance baseline case
            (100_000, 30),
            (1_000_000, 30)  # This matches the demo case
        ]

        results = []
        for docs, threshold in test_cases:
            result = self.run_test_and_measure(docs, threshold)
            if result:
                results.append(result)
                print(f"Completed test case: {docs} documents in {
                      result['execution_time']:.2f} seconds")
            else:
                print(f"Skipping remaining test cases due to timeout")
                break

        if results:
            self.generate_chart(results)

    @staticmethod
    def format_number(num):
        """Format large numbers to be more readable with K, M, B suffixes."""
        if num >= 1_000_000_000:
            return f"{num/1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return str(num)

    def generate_chart(self, results):
        doc_counts = [r['num_documents'] for r in results]
        execution_times = [r['execution_time'] for r in results]
        compressed_counts = [r['compressed_count'] for r in results]
        archived_counts = [r['archived_count'] for r in results]
        remaining_counts = [r['remaining_count'] for r in results]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 16))

        # Execution Time Chart
        ax1.plot(doc_counts, execution_times, marker='o')
        ax1.set_xscale('log')
        ax1.set_xlabel('Number of Documents')
        ax1.set_ylabel('Execution Time (seconds)')
        ax1.set_title('Execution Time vs. Number of Documents')

        # Format x-axis labels
        ax1.set_xticks(doc_counts)
        ax1.set_xticklabels([self.format_number(count)
                            for count in doc_counts])

        for i, txt in enumerate(execution_times):
            ax1.annotate(f"{txt:.2f}s", (doc_counts[i], execution_times[i]),
                         textcoords="offset points", xytext=(0, 10), ha='center')

        # Document Counts Chart
        width = 0.25
        x = np.arange(len(doc_counts))
        ax2.bar(x - width, compressed_counts, width, label='Compressed')
        ax2.bar(x, archived_counts, width, label='Archived')
        ax2.bar(x + width, remaining_counts, width, label='Remaining')
        ax2.set_xlabel('Number of Documents')
        ax2.set_ylabel('Number of Documents')
        ax2.set_title('Document Counts After Processing')
        ax2.set_xticks(x)

        # Format x-axis labels
        ax2.set_xticklabels([self.format_number(count)
                            for count in doc_counts])

        ax2.legend()

        # Format y-axis labels for the second chart
        ax2.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: self.format_number(x)))

        plt.tight_layout()
        plt.savefig('bank_balance_forward_performance.png')
        print("Chart saved as bank_balance_forward_performance.png")


if __name__ == '__main__':
    unittest.main()
