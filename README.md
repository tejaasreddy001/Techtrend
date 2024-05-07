#TechTrend - Streamlining Job Search 

In comparing our proposed solution with current advances in job boards, it becomes evident that traditional platforms have inherent limitations. The conventional model relies on job seekers to proactively identify and acquire the skills demanded by employers and apply for each jobs individually, resulting in a time-consuming and often inefficient process. The persistence of fraudulent job postings and the inability to ensure real-time accuracy in the job listings further amplify the challenges faced by both candidates and recruiters.
My proposed solution acknowledges these limitations and aims to usher in a paradigm shift by addressing the root causes of inefficiencies in the current system.

Please review the Final Project Report CPSC 597.pdf or Final Project Report CPSC 597.docx to know more about the project and architecture

Steps to run the project

To establish the Hadoop cluster and activate Apache Kafka for data ingestion, as well as Apache Zookeeper for resource management, follow these commands.

1. Install Angular, Flask, Hadoop and Setup MongoDB database in the techtrend.techtrend_user.json or echtrend.techtrend_user_db.json format.

2. Hadoop Setup
Install Hadoop, Apache Kafka and A
# start-all.sh
The following services are initiated:
• Data Node: Responsible for data storage within a Hadoop cluster node.
• JPS: Java Virtual Machine Process Status Tool to facilitate the listing of Java processes.
• Secondary Name Node: Executes periodic checkpoints for the Name Node in Hadoop.
• Resource Manager: Oversees resource management and application scheduling.
• Name Node: Manages the file system namespace and metadata for HDFS within Hadoop.
• Node Manager: Manages resources and containers on a node.

# zookeeper-server-start.sh $KAFKA_HOME/config/zookeeper.properties
Initiates the Zookeeper server crucial for Kafka to synchronize distributed processes.

# kafka-server-start.sh $KAFKA_HOME/config/server.properties
Launches the Kafka server, following the designated properties of configuration.

# kafka-topics.sh --create --topic resume_upload_topic --bootstrap-server localhost:9092 -- partitions 1 --replication-factor 1
Establishes a "resume_upload_topic" Kafka topic with specified replication factor and configuration parameters.

# kafka-console-producer.sh --topic resume_upload_topic --bootstrap-server localhost:9092
Initiates a console-based producer, allowing messages to be published to the Kafka topic "resume_upload_topic".

# kafka-console-consumer.sh --topic resume_upload_topic --bootstrap-server localhost:9092 -- from-beginning
Starts a consumer that makes it easier to retrieve messages from the "resume_upload_topic" Kafka topic right from the start.

# stop-all.sh
To stop all the services.

3. Changes in File

In app.py modify the following lines 

Add the path where you have stored your
resumeDataSet = pd.read_csv('/Users/tejaasmukundareddy/Documents/Final_Project/UpdatedResumeDataSet.csv', encoding='utf-8')

Add the path to your clf_model.pkl
clf = joblib.load('/Users/tejaasmukundareddy/Documents/Final_Project/clf_model.pkl')

Add the random resume  
uploaded_pdf_file = '/Users/tejaasmukundareddy/Documents/Home/Tejaas_Mukunda_Reddy.pdf'

Modify the url with your userid and password for mongodb database
atlas_uri = "mongodb+srv://userid:password&key/?retryWrites=true&w=majority&ssl_ca_certs=/path/to/cafile.pem"

Add the correct path
path = '/Users/tejaasmukundareddy/Documents/Final_Project/'
path = '/Users/tejaasmukundareddy/Documents/Final_Project/'



# Project Title

Brief description or overview of the project.

## Table of Contents

- [Project Title](#project-title)
- [About the Project](#about-the-project)
  - [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## About the Project

Explain in more detail what the project is about, its objectives, and its features.

### Built With

List the technologies/frameworks/languages used in the project.

- Technology/Framework/Language 1
- Technology/Framework/Language 2
- ...

## Getting Started

Provide instructions on how to get the project up and running on the local machine.

### Prerequisites

List any software, libraries, or dependencies needed before starting.

### Installation

Step-by-step guide on how to install/setup the project.

## Usage

Provide examples or instructions on how to use the project.

## Contributing

Guidelines for contributing to the project, including information on how to submit bug reports, feature requests, or pull requests.

## License

Information about the project's license.

## Contact

- [Author Name](author@example.com)
- Project Link: [Project Name](https://github.com/username/project-name)
