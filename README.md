# TechTrend - Streamlining Job Search 

Please review the Final Project Report CPSC 597.pdf or Final Project Report CPSC 597.docx to know more about the project and architecture

## About the Project

In comparing our proposed solution with current advances in job boards, it becomes evident that traditional platforms have inherent limitations. The conventional model relies on job seekers to proactively identify and acquire the skills demanded by employers and apply for each jobs individually, resulting in a time-consuming and often inefficient process. The persistence of fraudulent job postings and the inability to ensure real-time accuracy in the job listings further amplify the challenges faced by both candidates and recruiters. My proposed solution acknowledges these limitations and aims to usher in a paradigm shift by addressing the root causes of inefficiencies in the current system.

### Built With

- Angular
- Flask
- Hadoop
- MongoDB database 
- Python
- Beautiful Soup
- scikit-learn
- Colab

## Getting Started

1. Setup Hadoop, Apache Kafka and Apache Zookeeper 

- Command: start-all.sh
- The following services are initiated:
- Data Node: Responsible for data storage within a Hadoop cluster node.
- JPS: Java Virtual Machine Process Status Tool to facilitate the listing of Java processes.
- Secondary Name Node: Executes periodic checkpoints for the Name Node in Hadoop.
- Resource Manager: Oversees resource management and application scheduling.
- Name Node: Manages the file system namespace and metadata for HDFS within Hadoop.
- Node Manager: Manages resources and containers on a node.

- Command: zookeeper-server-start.sh $KAFKA_HOME/config/zookeeper.properties
- Initiates the Zookeeper server crucial for Kafka to synchronize distributed processes.

- Command: kafka-server-start.sh $KAFKA_HOME/config/server.properties
- Launches the Kafka server, following the designated properties of configuration.

- Command: kafka-topics.sh --create --topic resume_upload_topic --bootstrap-server localhost:9092 -- partitions 1 --replication-factor 1
- Establishes a "resume_upload_topic" Kafka topic with specified replication factor and configuration parameters.

- Command: kafka-console-producer.sh --topic resume_upload_topic --bootstrap-server localhost:9092
- Initiates a console-based producer, allowing messages to be published to the Kafka topic "resume_upload_topic".

- Command: kafka-console-consumer.sh --topic resume_upload_topic --bootstrap-server localhost:9092 -- from-beginning
- Starts a consumer that makes it easier to retrieve messages from the "resume_upload_topic" Kafka topic right from the start.

- Command: stop-all.sh
- To stop all the services.

2. Modify app.py file

- Add the path where you have stored your resume dataset:
- resumeDataSet = pd.read_csv('/Users/tejaasmukundareddy/Documents/Final_Project/UpdatedResumeDataSet.csv', encoding='utf-8')

- Add the path to your clf_model.pkl:
- clf = joblib.load('/Users/tejaasmukundareddy/Documents/Final_Project/clf_model.pkl')

- Add the path to the random resume:
- uploaded_pdf_file = '/Users/tejaasmukundareddy/Documents/Home/Tejaas_Mukunda_Reddy.pdf'

- Modify the URL with your userid and password for the MongoDB database:
- atlas_uri = "mongodb+srv://userid:password&key/?retryWrites=true&w=majority&ssl_ca_certs=/path/to/cafile.pem"

- Add the correct path:
- path = '/Users/tejaasmukundareddy/Documents/Final_Project/'
- path = '/Users/tejaasmukundareddy/Documents/Final_Project/'

### Prerequisites

- Angular
- Flask
- Hadoop
- Python - Environment with all dependencies for specified libraries
- Visual Studio Code
- MongoDB database
- Apache Kafka
- Apache ZooKeeper

## Usage

- Step 1: Download all the files or clone the repository
- Step 2: Follow the above steps for Hadoop, Apache Kafka and Apache Zookeeper setup and start all the services
- Step 3: Complete the setup for MongoDB atlas
- Step 4: Move to website folder and run # ng serve --open command and this will open up the website
- Step 5: Run the app.py code in dedicated terminal
- Step 6: Run the consumer.py code in dedicated terminal

Once you finish the preceding steps, you should be capable of executing the following operations.

From Candidate/User Perspective
- The User visits the Tech Trend Home Page and logs in.
- TechTrend fetches the current trending technologies data from the job board using web scraping.
- TechTrend returns the current trending technologies data to the User.
- The Users upload their resumes to TechTrend application.
- TechTrend analyzes the User's resume and displays Domain and ranking.
- The Users express interest in a company.
- TechTrend saves the User's company selection.
- TechTrend notifies the company's recruiters.
- The Users upload their certification to Tech Trend.
- TechTrend validates the certification.
- TechTrend saves the certification.
- The User emails a recruiter.

From Recruiter Perspective
- The Recruiter visits their Recruiter Page and logs in.
- TechTrend displays candidate profiles to the Recruiter.
- The Recruiter filters candidates by domain.
- The Recruiter filters the candidates based on ranking.
- TechTrend applies the filter and displays the candidates to the Recruiter.
- The Recruiter selects a candidate and TechTrend displays the email of the candidate.
- The Recruiter emails the candidate.

