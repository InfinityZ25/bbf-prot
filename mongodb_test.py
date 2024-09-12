import random
import time
from datetime import datetime, timedelta

from bson import ObjectId
from pymongo import ASCENDING, MongoClient

# Connect to the MongoDB replica set
client = MongoClient(
    'mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0')
db = client['your_database_name']


def seed_database(num_documents=1000000, batch_size=5000):
    # Clear existing data
    db.ledger_line_items.drop()

    start_date = datetime.utcnow() - timedelta(days=730)  # 2 years ago
    end_date = datetime.utcnow()

    batch = []
    for i in range(num_documents):
        doc = {
            'transactionDate': random_date(start_date, end_date),
            'amount': round(random.uniform(-10000, 10000), 2),
            'clientId': str(random.randint(0, 999)),
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
    threshold_date = datetime.utcnow() - timedelta(days=days_threshold)

    # Aggregation pipeline
    pipeline = [
        {
            '$match': {
                'transactionDate': {'$lt': threshold_date}
            }
        },
        {
            '$group': {
                '_id': None,
                'totalAmount': {'$sum': '$amount'},
                'transactionIds': {'$push': '$_id'},
                'minDate': {'$min': '$transactionDate'},
                'maxDate': {'$max': '$transactionDate'},
                'count': {'$sum': 1}
            }
        },
        {
            '$project': {
                '_id': {'$toString': {'$objectId': ''}},
                'compressionDate': datetime.utcnow(),
                'totalAmount': '$totalAmount',
                'originalTransactionIds': '$transactionIds',
                'transactionDateRange': {
                    'start': '$minDate',
                    'end': '$maxDate'
                },
                'transactionCount': '$count'
            }
        },
        {
            '$out': 'compressed_transactions'
        }
    ]

    # Perform aggregation
    result = list(db.ledger_line_items.aggregate(pipeline))

    # Create adjustment record
    last_compressed = db.compressed_transactions.find_one(
        sort=[('compressionDate', -1)])
    if last_compressed:
        adjustment_record = {
            'adjustmentDate': datetime.utcnow(),
            'resultingBalance': last_compressed['totalAmount']
        }
        db.adjustment_records.insert_one(adjustment_record)

    # Remove original transactions
    db.ledger_line_items.delete_many(
        {'transactionDate': {'$lt': threshold_date}})

    return {
        'compressed_count': last_compressed['transactionCount'] if last_compressed else 0,
        'total_amount': last_compressed['totalAmount'] if last_compressed else 0
    }


# Run the process
if __name__ == '__main__':
    # Seed the database
    print("Seeding the database...")
    seed_start_time = time.time()
    seed_database(num_documents=1000000, batch_size=5000)
    seed_end_time = time.time()
    print(f"Database seeded in {seed_end_time - seed_start_time:.2f} seconds")

    # Run the Bank Balance Forward process
    print("\\nRunning Bank Balance Forward process...")
    days_threshold = 30  # Adjust as needed

    start_time = time.time()
    result = bank_balance_forward(days_threshold)
    end_time = time.time()

    print(f"Bank Balance Forward process completed in {
          end_time - start_time:.2f} seconds")
    print(f"Compressed {result['compressed_count']} transactions")
    print(f"Total amount: {result['total_amount']}")
