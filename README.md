# Data-Engineering-Streaming-Project
## **Introduction: Building a Dynamic Data Engineering Project**

In our rapidly evolving digital age, data engineering has emerged as the backbone of the modern data-driven world. We're surrounded by an ever-increasing volume of data, and the ability to process and analyze this data in real-time is becoming a necessity rather than a luxury. In this guide, we'll delve deep into constructing a robust data pipeline, leveraging a combination of Kafka for data streaming, Spark for processing, Airflow for orchestration, Docker for containerization, S3 for storage, and Python as our primary scripting language.

To illustrate this process, we'll employ the Random Name API, a versatile tool that generates fresh random data every time it's triggered. It offers a practical representation of the real-time data many businesses deal with daily. The first step in our journey involves a Python script, designed meticulously to fetch data from this API. To emulate the streaming nature of data, we'll execute this script at regular intervals. But that's not all — this very script will also serve as our bridge to Kafka, writing the fetched data directly to a Kafka topic.

As we progress, Airflow's Directed Acyclic Graphs (DAGs) play a pivotal role. Orchestrating our processes, the Airflow DAG script ensures our Python script runs like clockwork, consistently streaming data and feeding it into our pipeline. Once our data makes its way to the Kafka producer, Spark Structured Streaming takes the baton. It consumes this data, processes it, and then seamlessly writes the modified data to S3, ensuring it's ready for any subsequent analytical processes.

An essential aspect of our project is its modular architecture. Each service, be it Kafka, Spark, or Airflow, runs in its isolated environment, thanks to Docker containers. This not only ensures smooth interoperability but also simplifies scalability and debugging.

## **Getting Started: Prerequisites and Setup**

For this project, we are leveraging a GitHub repository that hosts our entire setup, making it easy for anyone to get started.

**a. Docker:**
Docker will be our primary tool to orchestrate and run various services.

- **Installation:** Visit Docker's official website to download and install Docker Desktop for your OS.
- **Verification:** Open a terminal or command prompt and execute `docker --version` to ensure a successful installation.

**b. S3:**
AWS S3 is our go-to for data storage.

- **Setup:** Log in to the AWS Management Console, navigate to the S3 service, and establish a new bucket, ensuring it's configured according to your data storage preferences.

**c. Setting Up the Project:**

- **Clone the Repository:** First, you'll need to clone the project from its GitHub repository using the following command:

```
git clone <https://github.com/simardeep1792/Data-Engineering-Streaming-Project.git>
```

Navigate to the project directory:

```
cd Data-Engineering-Streaming-Project
```

- **Deploy Services using `docker-compose`:** Within the project directory, you'll find a `docker-compose.yml` file. This file describes all the services and their

```
docker network create docker_streaming
docker-compose -f docker-compose.yml up -d
```

This command orchestrates the start-up of all necessary services like Kafka, Spark, Airflow, etc., in Docker containers.

## **Breaking Down the projects Files**

### 1)  ****`docker-compose.yml`**

The heart of our project setup lies in the **`docker-compose.yml`** file. It orchestrates our services, ensuring smooth communication and initialization. Here's a breakdown:

**1. Version**

We're using Docker Compose file format version '3.7', ensuring compatibility with our services.

**2. Services**

Our project encompasses several services:

- **Airflow:**
- **Database (`airflow_db`):** Uses PostgreSQL[1](https://github.com/simardeep1792/Data-Engineering-Streaming-Project#:~:text=%E3%80%9059%E2%80%A0.env%E3%80%91%0A%0A%E3%80%9060%E2%80%A0README.md%E3%80%91%0A%0A%E3%80%9061%E2%80%A0airflow.sh%E3%80%91%0A%0A%E3%80%9062%E2%80%A0docker).
- **Web Server (`airflow_webserver`):** Initiates the database and sets up an admin user.
- **Kafka:**
- **Zookeeper (`kafka_zookeeper`):** Manages broker metadata.
- **Brokers:** Three instances (**`kafka_broker_1`**, **`2`**, and **`3`**).
- **Base Configuration (`kafka_base`):** Common settings for brokers.
- **Kafka Connect (`kafka_connect`):** Facilitates stream processing.
- **Schema Registry (`kafka_schema_registry`):** Manages Kafka schemas.
- **User Interface (`kafka_ui`):** Visual interface for Kafka insights.
- **Spark:**
- **Master Node (`spark_master`):** The central control node for Apache Spark.

**3. Volumes**

We utilize a persistent volume, **`spark_data`**, ensuring data consistency for Spark.

**4. Networks**

Two networks anchor our services:

- **Kafka Network (`kafka_network`):** Dedicated to Kafka.
- **Default Network (`default`):** Externally named as **`docker_streaming`**.

### 2)  **`kafka_stream_dag.py`**

This file primarily defines an Airflow Directed Acyclic Graph (DAG) that handles the streaming of data to a Kafka topic.

**1. Imports**

Essential modules and functions are imported, notably the Airflow DAG and PythonOperator, as well as a custom **`initiate_stream`** function from **`kafka_streaming_service`**.

**2. Configuration**

- **DAG Start Date (`DAG_START_DATE`):** Sets when the DAG begins its execution.
- **Default Arguments (`DAG_DEFAULT_ARGS`):** Configures the DAG's basic parameters, such as owner, start date, and retry settings.

**3. DAG Definition**

A new DAG is created with the name **`name_stream_dag`**, configured to run daily at 1 AM. It's designed not to run for any missed intervals (with **`catchup=False`**) and allows only one active run at a time.

**4. Tasks**

A single task, **`kafka_stream_task`**, is defined using the PythonOperator. This task calls the **`initiate_stream`** function, effectively streaming data to Kafka when the DAG runs.

### 3)  **`kafka_streaming_service.py`**

**1. Imports & Configuration**

Essential libraries are imported, and constants are set, such as the API endpoint, Kafka bootstrap servers, topic name, and streaming interval details.

**2. User Data Retrieval**

The **`retrieve_user_data`** function fetches random user details from the specified API endpoint.

**3. Data Transformation**

The **`transform_user_data`** function formats the raw user data for Kafka streaming, while **`encrypt_zip`** hashes the zip code to maintain user privacy.

**4. Kafka Configuration & Publishing**

- **`configure_kafka`** sets up a Kafka producer.
- **`publish_to_kafka`** sends transformed user data to a Kafka topic.
- **`delivery_status`** provides feedback on whether data was successfully sent to Kafka.

**5. Main Streaming Function**

**`initiate_stream`** orchestrates the entire process, retrieving, transforming, and publishing user data to Kafka at regular intervals.

**6. Execution**

When the script is run directly, the **`initiate_stream`** function is executed, streaming data for the duration specified by **`STREAMING_DURATION`**.

### 3)  **`spark_processing.py`**

**1. Imports & Logging Initialization**

The necessary libraries are imported, and a logging setup is created for better debugging and monitoring.

**2. Spark Session Initialization**

**`initialize_spark_session`**: This function sets up the Spark session with configurations required to access data from S3.

**3. Data Retrieval & Transformation**

- **`get_streaming_dataframe`**: Fetches a streaming dataframe from Kafka with specified brokers and topic details.
- **`transform_streaming_data`**: Transforms the raw Kafka data into a desired structured format.

**4. Streaming to S3**

**`initiate_streaming_to_bucket`**: This function streams the transformed data to an S3 bucket in parquet format. It uses a checkpoint mechanism to ensure data integrity during streaming.

**5. Main Execution**

The **`main`** function orchestrates the entire process: initializing the Spark session, fetching data from Kafka, transforming it, and streaming it to S3.

**6. Script Execution**

If the script is the main module being run, it will execute the **`main`** function, initiating the entire streaming process.

## **Building the Data Pipeline: Step-by-Step**

### **1. Set Up Kafka Cluster**

Start your Kafka cluster with the following commands:

```bash
docker network create docker_streaming
docker-compose -f docker-compose.yml up -d
```

### 2**. Create the topic for Kafka (**http://localhost:8888/)

- Access the Kafka UI at http://localhost:8888/.
- Observe the active cluster.
- Navigate to 'Topics'.
- Create a new topic named "names_topic".
- Set the replication factor to 3.

### 3**. Configure Airflow User**

Create an Airflow user with admin privileges:

```bash
docker-compose run airflow_webserver airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin
```

### 4**. Access Airflow Bash & Install Dependencies**

Use the provided script to access the Airflow bash and install required packages:

```bash
./airflow.sh bash
pip install -r ./requirements.txt
```

### 5**. Validate DAGs**

Ensure there are no errors with your DAGs:

```bash
airflow dags list
```

### 6**. Start Airflow Scheduler**

To initiate the DAG, run the scheduler:

```bash
airflow scheduler
```

### 6**. Verify the data is uploaded to Kafka Cluster**

- Access the Kafka UI at http://localhost:8888/ and verify that the data is uploaded for the topic

### 8**. Transfer Spark Script**

Copy your Spark script into the Docker container:

```bash
docker cp spark_processing.py spark_master:/opt/bitnami/spark/
```

### 9**. Initiate Spark Master & Download JARs**

Access Spark bash, navigate to the `jars` directory, and download essential JAR files. After downloading, submit the Spark job:

```bash
docker exec -it spark_master /bin/bash
cd jars

curl -O https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/2.8.1/kafka-clients-2.8.1.jar
curl -O https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.13/3.3.0/spark-sql-kafka-0-10_2.13-3.3.0.jar
curl -O https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.2.0/hadoop-aws-3.2.0.jar
curl -O https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-s3/1.11.375/aws-java-sdk-s3-1.11.375.jar
curl -O https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.8.0/commons-pool2-2.8.0.jar

cd ..
spark-submit \
--master local[2] \
--jars /opt/bitnami/spark/jars/kafka-clients-2.8.1.jar,\
/opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.13-3.3.0.jar,\
/opt/bitnami/spark/jars/hadoop-aws-3.2.0.jar,\
/opt/bitnami/spark/jars/aws-java-sdk-s3-1.11.375.jar,\
/opt/bitnami/spark/jars/commons-pool2-2.8.0.jar \
spark_processing.py
```

### 10**. Verify Data on S3**

After executing the steps, check your S3 bucket to ensure data has been uploaded

## C**hallenges and Troubleshooting**

1. **Configuration Challenges**: Ensuring environment variables and configurations (like in the **`docker-compose.yaml`** file) are correctly set can be tricky. An incorrect setting might prevent services from starting or communicating.
2. **Service Dependencies**: Services like Kafka or Airflow have dependencies on other services (e.g., Zookeeper for Kafka). Ensuring the correct order of service initialization is crucial.
3. **Airflow DAG Errors**: Syntax or logical errors in the DAG file (**`kafka_stream_dag.py`**) can prevent Airflow from recognizing or executing the DAG correctly.
4. **Data Transformation Issues**: The data transformation logic in the Python script might not always produce expected results, especially when handling various data inputs from the Random Name API.
5. **Spark Dependencies**: Ensuring all required JARs are available and compatible is essential for Spark's streaming job. Missing or incompatible JARs can lead to job failures.
6. **Kafka Topic Management**: Creating topics with the correct configuration (like replication factor) is essential for data durability and fault tolerance.
7. **Networking Challenges**: Docker networking, as set up in the **`docker-compose.yaml`**, must correctly facilitate communication between services, especially for Kafka brokers and Zookeeper.
8. **S3 Bucket Permissions**: Ensuring correct permissions when writing to S3 is crucial. Misconfigured permissions can prevent Spark from saving data to the bucket.
9. **Deprecation Warnings**: The provided logs show deprecation warnings, indicating that some methods or configurations used might become obsolete in future versions.

## **Conclusion:**

Throughout this journey, we delved deep into the intricacies of real-world data engineering, progressing from raw, unprocessed data to actionable insights. Beginning with collecting random user data, we harnessed the capabilities of Kafka, Spark, and Airflow to manage, process, and automate the streaming of this data. Docker streamlined the deployment, ensuring a consistent environment, while other tools like S3 and Python played pivotal roles.

This endeavor was more than just constructing a pipeline; it was about understanding the synergy between tools. I encourage all readers to experiment further, adapting and enhancing this pipeline to cater to unique requirements and uncover even more profound insights. Dive in, explore, and innovate!