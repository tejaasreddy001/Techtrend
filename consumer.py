from confluent_kafka import Consumer, KafkaError
from hdfs import InsecureClient
print("checking")
# Initialize Kafka consumer
consumer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': '123',  # Set your group ID here
    'auto.offset.reset': 'earliest',
}
consumer = Consumer(consumer_conf)
# Subscribing the kafka consumer topic
consumer.subscribe(['resume_upload_topic'])
# Initialize HDFS client
hdfs_client = InsecureClient('http://localhost:9870', user='tejaasmukundareddy')
try:
    while True:
        msg = consumer.poll(1.0) 
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break
        user_id = msg.key().decode('utf-8')
        resume_data = msg.value()
        # Delete existing resume in HDFS with the same user_id
        hdfs_existing_path = f'/path/to/resumes/{user_id}.pdf'
        hdfs_client.delete(hdfs_existing_path, recursive=True)
        # Write the new resume to HDFS with the user_id as the filename
        hdfs_new_path = f'/path/to/resumes/{user_id}.pdf'
        with hdfs_client.write(hdfs_new_path) as hdfs_file:
            hdfs_file.write(resume_data)
            print(f"Resume for user {user_id} written to HDFS")
except KeyboardInterrupt:
    pass
finally:
    # Close down consumer to commit final offsets.
    consumer.close()
