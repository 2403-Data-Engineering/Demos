import Dependencies._

ThisBuild / scalaVersion     := "2.13.16"
ThisBuild / version          := "0.1.0-SNAPSHOT"
ThisBuild / organization     := "com.example"
ThisBuild / organizationName := "example"
Compile / mainClass := Some("example.Main")

lazy val root = (project in file("."))
  .settings(
    name := "demo-1",
    libraryDependencies += munit % Test,
    libraryDependencies += "org.apache.spark" %% "spark-sql" % "4.0.0"
  )

// See https://www.scala-sbt.org/1.x/docs/Using-Sonatype.html for instructions on how to publish to Sonatype.
