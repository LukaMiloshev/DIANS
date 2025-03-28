from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, avg, min, max, sum, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
from cassandra.cluster import Cluster
import psycopg2

KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "financial_data"

PG_HOST = "localhost"
PG_DB = "financial_data"
PG_USER = "postgres"
PG_PASSWORD = "your_password"

CASSANDRA_HOSTS = ["127.0.0.1"]
CASSANDRA_KEYSPACE = "financial"

spark = SparkSession.builder \
    .appName("RealTimeProcessing") \
    .config("spark.sql.streaming.schemaInference", "true") \
    .getOrCreate()

schema = StructType([
    StructField("source", StringType(), True),
    StructField("symbol", StringType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("volume", DoubleType(), True)
])

raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

parsed_stream = raw_stream.selectExpr("CAST(value AS STRING) as json_data") \
    .select(from_json(col("json_data"), schema).alias("data")) \
    .select("data.*")

processed_stream = parsed_stream.withColumn("timestamp", col("timestamp").cast(TimestampType())) \
    .withColumn("timestamp", col("timestamp").otherwise(current_timestamp()))

filtered_stream = processed_stream.filter(col("symbol").isNotNull())

aggregated_stream = filtered_stream.groupBy("symbol") \
    .agg(
        avg("close").alias("avg_close"),
        min("low").alias("min_low"),
        max("high").alias("max_high"),
        sum("volume").alias("total_volume")
    )

def write_to_postgres(batch_df, batch_id):
    conn = psycopg2.connect(
        host=PG_HOST, database=PG_DB, user=PG_USER, password=PG_PASSWORD
    )
    cursor = conn.cursor()
    for row in batch_df.collect():
        cursor.execute(
            "INSERT INTO aggregated_data (symbol, avg_close, min_low, max_high, total_volume) VALUES (%s, %s, %s, %s, %s)"
            "ON CONFLICT (symbol) DO UPDATE SET avg_close = EXCLUDED.avg_close, min_low = EXCLUDED.min_low, max_high = EXCLUDED.max_high, total_volume = EXCLUDED.total_volume",
            (row.symbol, row.avg_close, row.min_low, row.max_high, row.total_volume)
        )
    conn.commit()
    cursor.close()
    conn.close()

def write_to_cassandra(batch_df, batch_id):
    cluster = Cluster(CASSANDRA_HOSTS)
    session = cluster.connect()
    session.set_keyspace(CASSANDRA_KEYSPACE)
    for row in batch_df.collect():
        session.execute(
            "INSERT INTO aggregated_data (symbol, avg_close, min_low, max_high, total_volume) VALUES (%s, %s, %s, %s, %s)",
            (row.symbol, row.avg_close, row.min_low, row.max_high, row.total_volume)
        )
    cluster.shutdown()

query = aggregated_stream.writeStream \
    .outputMode("complete") \
    .foreachBatch(lambda df, epoch: (write_to_postgres(df, epoch), write_to_cassandra(df, epoch))) \
    .start()

query.awaitTermination()
