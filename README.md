#TechTrend - Streamlining Job Search 

In comparing our proposed solution with current advances in job boards, it becomes evident that traditional platforms have inherent limitations. The conventional model relies on job seekers to proactively identify and acquire the skills demanded by employers and apply for each jobs individually, resulting in a time-consuming and often inefficient process. The persistence of fraudulent job postings and the inability to ensure real-time accuracy in the job listings further amplify the challenges faced by both candidates and recruiters.
My proposed solution acknowledges these limitations and aims to usher in a paradigm shift by addressing the root causes of inefficiencies in the current system.

Please review the Final Project Report CPSC 597.pdf or Final Project Report CPSC 597.docx to know more about the project and architecture

Steps to run the project

To establish the Hadoop cluster and activate Apache Kafka for data ingestion, as well as Apache Zookeeper for resource management, follow these commands.
1. Hadoop Setup
# start-all.sh
a. The following services are initiated:
• Data Node: Responsible for data storage within a Hadoop cluster node.
• JPS: Java Virtual Machine Process Status Tool to facilitate the listing of Java processes.
• Secondary Name Node: Executes periodic checkpoints for the Name Node in Hadoop.
• Resource Manager: Oversees resource management and application scheduling.
• Name Node: Manages the file system namespace and metadata for HDFS within Hadoop.
• Node Manager: Manages resources and containers on a node.
2. # zookeeper-server-start.sh $KAFKA_HOME/config/zookeeper.properties
a. Initiates the Zookeeper server crucial for Kafka to synchronize distributed processes.
3. # kafka-server-start.sh $KAFKA_HOME/config/server.properties
a. Launches the Kafka server, following the designated properties of configuration.
4. # kafka-topics.sh --create --topic resume_upload_topic --bootstrap-server localhost:9092 -- partitions 1 --replication-factor 1
a. Establishes a "resume_upload_topic" Kafka topic with specified replication factor and configuration parameters.
5. # kafka-console-producer.sh --topic resume_upload_topic --bootstrap-server localhost:9092
a. Initiates a console-based producer, allowing messages to be published to the Kafka topic
"resume_upload_topic".
6. # kafka-console-consumer.sh --topic resume_upload_topic --bootstrap-server localhost:9092 -- from-beginning
a. Starts a consumer that makes it easier to retrieve messages from the "resume_upload_topic" Kafka topic right from the start.
7. # stop-all.sh
a. To stop all the services.

 
