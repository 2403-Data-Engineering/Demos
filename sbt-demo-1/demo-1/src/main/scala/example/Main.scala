package example

import java.io.PrintWriter
import scala.util.Random

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

object Main {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("SparkDemo")
      .master("local[*]")
      .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    import spark.implicits._

    // createData()


    val df = spark.read
      .option("header", "true")
      .option("inferSchema", "true")
      .csv("data/sales.csv")


    println("Base DF: ")

    println(s"Row count: ${df.count()}")
    println(s"Partition count: ${df.rdd.getNumPartitions}")


    //narrow transformations: Map, FlapMap, Filer, coalesce(?), withColumn, select
    df.filter($"amount" > 5.0) //narrow, no shuffle
      .withColumn("amount_cents", ($"amount" * 100).cast("int"))
      .select($"id", $"region", $"product", $"amount_cents")
      .filter($"region" === "North")
      .write
      .mode("overwrite")
      .option("header", "true")
      .parquet("data/parquet/")

    val wide = df.filter($"amount" > 5.0) //narrow, no shuffle
      .withColumn("amount_cents", ($"amount" * 100).cast("int")) //narrow, no shuffle
      .select($"region", $"amount_cents") //narrow, no shuffle
      .groupBy($"region") // WIDE! Shuffle incoming!
      .agg(
        sum($"amount_cents").alias("total_in_pennies")// WIDE! Shuffle incoming!
      )


    wide.explain()

    // println("Repartition: ")
    // val repartitioned = df.repartition(8)
    // println(s"After repartition(8): ${repartitioned.rdd.getNumPartitions}")

    // println("Coalesce: ")
    // val coalesced = df.coalesce(2)
    // println(s"After coalesce(2): ${coalesced.rdd.getNumPartitions}")


    println("Done")
    spark.stop()

  }

  def createData(): Unit = {
    val pw = new PrintWriter("data/sales.csv")
    pw.println("id,region,product,amount")
    val regions = Seq("North", "South", "East", "West")
    val products = Seq("Widget", "Gadget", "Gizmo", "Doohickey")
    val rng = new Random(42)
    for (i <- 1 to 500000) {
      val region = regions(rng.nextInt(regions.length))
      val product = products(rng.nextInt(products.length))
      val amount = (rng.nextDouble() * 1000).round / 100.0
      pw.println(s"$i,$region,$product,$amount")
    }
    pw.close()
  }
}