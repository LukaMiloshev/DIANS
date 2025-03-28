from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, avg, min, max, sum, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "financial_data"

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

query = aggregated_stream.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

query.awaitTermination()
