"""
Bank Balance Forward (BBF) Demo Module

This module implements a bank balance forward operation for a simulated banking system.
It includes functions for seeding a database with transaction data, performing balance
forward calculations, and managing ledger line items.

Key components:
- seed_database: Populates the database with sample transaction data.
- bank_balance_forward: Performs the balance forward operation based on a time threshold.
- Various utility functions for date manipulation and data generation.

The module interacts with a MongoDB database to store and process financial transactions.
"""
import random
from datetime import UTC, datetime, timedelta

from bson import ObjectId
from pymongo import ASCENDING, MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['items']


def seed_database(num_documents=1000000, batch_size=5000):
    """
    Seed the database with a specified number of documents.

    This function clears existing data in the ledger_line_items collection
    and populates it with new randomly generated documents.

    Args:
        num_documents (int): The total number of documents to insert.
                             Defaults to 1,000,000.
        batch_size (int): The number of documents to insert in each batch.
                          Defaults to 5,000.

    Returns:
        None

    Side effects:
        - Drops the existing ledger_line_items collection.
        - Inserts new documents into the ledger_line_items collection.
    """
    # Clear existing data
    db.ledger_line_items.drop()

    start_date = datetime.now(UTC) - timedelta(days=730)  # 2 years ago
    end_date = datetime.now(UTC)

    batch = []
    for i in range(num_documents):
        doc = {
            'transactionDate': random_date(start_date, end_date),
            'amount': round(random.uniform(-10000, 10000), 2),
            'clientId': str(random.randint(0, 999)),
            'productId': str(random.randint(0, 99)),
            'category': random.choice(['Business', 'Tax', 'Personal']),
            'status': random.choice(['Pending', 'Completed', 'Cancelled'])
        }
        batch.append(doc)

        if len(batch) == batch_size or i == num_documents - 1:
            db.ledger_line_items.insert_many(batch)
            batch = []
            print(f"Inserted {i + 1} documents")

    # Create an index on transactionDate for better query performance
    db.ledger_line_items.create_index([('transactionDate', ASCENDING)])

    print(f"Data generation complete. Total documents: {
          db.ledger_line_items.count_documents({})}")


def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))


def bank_balance_forward(days_threshold):
    """
    Perform a bank balance forward operation based on a given threshold of days.

    This function processes ledger line items, marking old entries for deletion
    and calculating new balances for accounts based on recent transactions.

    Args:
        days_threshold (int): The number of days to look back. Transactions
                              older than this will be marked for deletion.

    Returns:
        None

    Side effects:
        - Marks old ledger entries for deletion in the database.
        - Updates account balances based on recent transactions.
        - May modify the ledger_line_items and accounts collections in the database.
    """
    threshold_date = datetime.now(UTC) - timedelta(days=days_threshold)
    deletion_mark = ObjectId()  # Generate a unique ID for this batch of deletions

    # Pipeline for compressing transactions
    compress_pipeline = [
        {
            '$match': {
                'transactionDate': {'$lt': threshold_date}
            }
        },
        {
            '$group': {
                '_id': '$clientId',  # Group by clientId
                'totalAmount': {'$sum': '$amount'},
                'transactionCount': {'$sum': 1},
                'firstTransactionDate': {'$min': '$transactionDate'},
                'lastTransactionDate': {'$max': '$transactionDate'},
                # Collect all unique productIds
                'products': {'$addToSet': '$productId'}
            }
        },
        {
            '$project': {
                '_id': 0,
                'clientId': '$_id',
                'compressionDate': datetime.now(UTC),
                'totalAmount': '$totalAmount',
                'transactionCount': '$transactionCount',
                'dateRange': {
                    'start': '$firstTransactionDate',
                    'end': '$lastTransactionDate'
                },
                'products': 1
            }
        },
        {
            '$merge': {
                'into': 'compressed_transactions',
                'whenMatched': 'replace',
                'whenNotMatched': 'insert'
            }
        }
    ]

    # Pipeline for marking transactions for deletion
    mark_pipeline = [
        {
            '$match': {
                'transactionDate': {'$lt': threshold_date}
            }
        },
        {
            '$addFields': {
                'mark_for_deletion_id': deletion_mark
            }
        },
        {
            '$merge': {
                'into': 'ledger_line_items',
                'whenMatched': 'merge',
                'whenNotMatched': 'discard'
            }
        }
    ]

    # Pipeline for archiving marked transactions
    archive_pipeline = [
        {
            '$match': {
                'mark_for_deletion_id': deletion_mark
            }
        },
        {
            '$out': 'archived_items'
        }
    ]

    # Execute compress pipeline
    db.ledger_line_items.aggregate(compress_pipeline)

    # Execute mark pipeline
    db.ledger_line_items.aggregate(mark_pipeline)

    # Execute archive pipeline
    db.ledger_line_items.aggregate(archive_pipeline)

    # Remove archived documents from the main collection using the deletion mark
    delete_result = db.ledger_line_items.delete_many(
        {'mark_for_deletion_id': deletion_mark})

    # Get results
    compressed_count = db.compressed_transactions.count_documents({})
    archived_count = db.archived_items.count_documents({})
    remaining_count = db.ledger_line_items.count_documents({})

    return {
        'compressed_count': compressed_count,
        'archived_count': archived_count,
        'deleted_count': delete_result.deleted_count,
        'remaining_count': remaining_count
    }


# Run the process
if __name__ == '__main__':
    # Seed the database (uncomment if you need to generate new data)
    print("Seeding the database...")
    seed_start_time = datetime.now(UTC)
    seed_database(num_documents=1000000, batch_size=5000)
    seed_end_time = datetime.now(UTC)
    print(f"Database seeded in {
          (seed_end_time - seed_start_time).total_seconds():.2f} seconds")

    print("\\nRunning Bank Balance Forward process...")
    days_threshold = 30  # Adjust as needed

    start_time = datetime.now(UTC)
    result = bank_balance_forward(days_threshold)
    end_time = datetime.now(UTC)

    print(f"Bank Balance Forward process completed in {
          (end_time - start_time).total_seconds():.2f} seconds")
    print(f"Compressed {result['compressed_count']} transactions")
    print(f"Archived {result['archived_count']} original transactions")
    print(f"Deleted {result['deleted_count']
                     } transactions from main collection")
    print(f"Remaining transactions in main collection: {
          result['remaining_count']}")
