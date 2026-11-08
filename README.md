# Algae Cultivation Data Engineering Platform

### Python | SQLite | FastAPI | Pandas | OpenPyXL | Plotly.js | Data Engineering

**Arizona State University — Arizona Center for Algae Technology and Innovation (AzCATI)**

A research data engineering platform designed to automate the ingestion, organization, validation, and analysis of environmental sensor and laboratory data from algae cultivation experiments.

The platform supports the processing and integration of historical research datasets collected over more than six years, helping transform fragmented experimental records into structured, consistent, and accessible information.

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest -q

# Generate synthetic demo data
python -m demo.generate_synthetic_data

# Run the end-to-end demo
python -m demo.run_demo

# Optional: generate sensor QC plot
python -m demo.plot_demo
```

> Run all commands from the repository root.


## Project Overview

Large-scale algae cultivation research generates substantial amounts of data from multiple sources, including environmental sensors, laboratory measurements, microscopy observations, and experimental records.

These datasets are often stored in separate Excel workbooks with different formats, naming conventions, timestamps, and data-quality issues.

Manually organizing and validating the data is time-consuming and increases the risk of inconsistencies.

This project addresses these challenges through automated data processing, a centralized experiment registry, quality-control algorithms, and interactive validation tools.

### Project Objectives

- Automate ingestion and standardization of historical experimental datasets.
- Organize experiment metadata in a relational database.
- Identify and investigate sensor anomalies and structural data errors.
- Associate measurements with the correct experiments.
- Reconcile inconsistent strain identifiers across datasets.
- Provide interactive visualization and validation tools.
- Improve the reliability of research data for downstream analysis.

---

## Key Features

### 1. SQLite Experiment Registry

Developed a SQLite-backed experiment registry containing more than 160 experiments.

The registry helps organize experimental metadata and associate records from different research data sources.

**Key capabilities:**

- Structured storage of experiment information.
- Identification and organization of experimental records.
- Support for linking sensor, laboratory, and microscopy datasets.
- Consistent experiment identification across processing workflows.
- Database-backed lookup for data integration tasks.

**Technologies:** Python, SQLite, SQL

### 2. Automated YSI Sensor Data Processing

Developed a Python processing pipeline for environmental sensor measurements collected from more than 20 pond sensors.

The pipeline processes raw Excel workbooks and generates standardized time-series CSV files.

**Key capabilities:**

- Excel/XLSX data ingestion.
- Extraction of environmental sensor measurements.
- Detection and correction of column-shift artifacts.
- Standardization of sensor data.
- Processing of historical time-series measurements.
- Generation of cleaned CSV outputs for validation and analysis.

Environmental measurements include:

- pH
- Dissolved oxygen
- Temperature
- Conductivity
- Salinity
- Oxidation-reduction potential (ORP)

**Technologies:** Python, Pandas, OpenPyXL

### 3. Automated Sensor Quality Control

Implemented data-quality procedures to identify potentially inaccurate or unreliable sensor measurements.

The quality-control layer supports 15-minute interval time-series data.

**Quality-control capabilities:**

**Physical bounds validation**

Flags measurements outside configured physical or expected operating ranges.

**Flat-line and stuck-sensor detection**

Identifies prolonged periods of constant readings that may indicate sensor malfunction or measurement problems.

**Missing-data and gap visualization**

Supports identification of missing readings and interruptions in sensor measurements.

**Data standardization**

Produces structured outputs that can be compared across experimental datasets.

The purpose of these checks is to make questionable measurements visible and easier to investigate rather than assume all raw readings are valid.

**Technologies:** Python, Pandas, time-series processing

### 4. Automated Microscopy Experiment Matching

Developed an experiment-matching pipeline, referred to as microsort, to reconcile microscopy observations with experimental metadata.

Research records may use inconsistent strain names, abbreviations, or identifiers.

The matching workflow uses a standardized strain taxonomy bank and fuzzy matching to improve consistency.

**Key capabilities:**

- Strain-name normalization.
- Fuzzy matching of inconsistent identifiers.
- Experiment metadata lookup.
- Reconciliation of microscopy observations with experiment records.
- Support for linking microscopy data to the broader research dataset.

**Technologies:** Python, SQLite, fuzzy matching, data normalization

### 5. Interactive Web-Based Validation Tool

Developed an interactive validation interface using Plotly.js to evaluate processed sensor data against reference Excel workbooks.

The tool helps assess whether pipeline-generated measurements align with reference datasets.

**Key capabilities:**

- Interactive visualization of sensor measurements.
- Comparison of processed and reference time-series data.
- Per-sensor alignment scoring.
- Identification of potential discrepancies.
- Support for visual inspection and validation of experimental data.

The interface helps make technical data-validation results more accessible and understandable.

**Technologies:** JavaScript, Plotly.js, Python, Excel data processing

---

## System Architecture

The platform consists of multiple data-processing and validation components.

### High-Level Data Flow

```text
          RESEARCH DATA SOURCES
                    |
       +------------+------------+
       |            |            |
   YSI Sensor   Laboratory   Microscopy
   Excel Files   Records     Observations
       |            |            |
       v            v            v
  Sensor Data    Experiment    Microscopy
  Processing     Metadata      Matching
       |            |            |
       v            v            v
  Data Cleaning   SQLite      Strain Taxonomy
  and Sensor QC   Registry    and Fuzzy Matching
       |            |            |
       +------------+------------+
                    |
                    v
       Structured Research Data
                    |
                    v
       Interactive Validation
         and Visualization
                    |
                    v
       Data Quality Review
       and Downstream Analysis
```

*This diagram is a conceptual overview of the project's major components rather than a complete deployment architecture.*

---

## Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python, JavaScript, HTML, CSS |
| Backend Development | FastAPI, REST APIs |
| Database | SQLite, SQL |
| Data Processing | Pandas, NumPy, OpenPyXL |
| Data Visualization | Plotly.js |
| Data Integration | Fuzzy matching, metadata reconciliation |
| Data Quality | Bounds checking, sensor fault detection, gap analysis |
| Development Practices | Git, data validation, testing |

---

## Engineering Challenges and Solutions

### Challenge 1: Inconsistent Excel File Structures

**Problem:**

Historical sensor workbooks may contain structural inconsistencies, including column-shift artifacts that affect the interpretation of measurements.

**Approach:**

Developed processing logic to detect and correct identified column-shift artifacts before generating standardized datasets.

**Engineering significance:**

Demonstrates automated file processing, defensive programming, and validation of imperfect real-world data.

### Challenge 2: Faulty Environmental Sensor Measurements

**Problem:**

Environmental monitoring systems may generate implausible measurements, extended constant readings, or incomplete time series.

**Approach:**

Implemented quality-control procedures involving physical bounds, flat-line detection, and gap visualization.

**Engineering significance:**

Demonstrates rule-based anomaly detection, time-series data processing, and data reliability engineering.

### Challenge 3: Inconsistent Experimental Identifiers

**Problem:**

Microscopy and experimental records may use different naming conventions for the same strains or experiments.

**Approach:**

Developed normalization and fuzzy-matching workflows supported by experiment metadata and a standardized strain taxonomy bank.

**Engineering significance:**

Demonstrates entity resolution, automated record matching, and integration of heterogeneous data sources.

### Challenge 4: Verifying Processed Data

**Problem:**

An automated data-processing pipeline must be validated to ensure that its outputs are consistent with reference measurements.

**Approach:**

Built an interactive Plotly.js interface for comparing processed YSI measurements against reference Excel data and reviewing per-sensor alignment scores.

**Engineering significance:**

Demonstrates validation tooling, interactive web development, and data-driven quality assessment.

---

## Project Scope

The research environment includes:

- More than six years of historical algae cultivation research data.
- A SQLite experiment registry tracking 160+ experiments.
- Environmental measurements from more than 20 pond sensors.
- Time-series measurements collected at 15-minute intervals.
- Multiple data sources, including sensors, laboratory records, and microscopy observations.
- Automated processing, matching, quality-control, and validation workflows.

These figures describe different aspects of the research environment and should not be interpreted as the total number of fully processed or validated experiments.

---

## My Contributions

As a Graduate Research Assistant working with ASU's AzCATI research environment, my software engineering contributions include:

- Developing Python-based data ingestion and processing workflows.
- Implementing automated sensor-quality checks.
- Working on database-backed experiment organization and metadata integration.
- Engineering microscopy experiment-matching functionality.
- Developing interactive web-based data-validation tools.
- Supporting integration of heterogeneous research datasets.
- Translating research data challenges into practical software workflows.

---

## Relevance to AI and Intelligent Automation

Although this project is primarily focused on data engineering rather than deploying a large language model, it establishes several foundations relevant to AI-enabled applications.

These include:

- Structured and searchable data.
- Automated ingestion of heterogeneous files.
- Data-quality validation.
- Entity matching and metadata reconciliation.
- Reliable preparation of datasets for downstream analytics.
- Interfaces that make complex information accessible to users.

These engineering capabilities can support future machine learning, predictive modeling, and AI-assisted research applications.

Potential future applications include sensor anomaly prediction, experimental productivity forecasting, and natural-language interfaces for exploring research records.

These are potential extensions, not claimed completed features.

---

## What I Learned

This project strengthened my understanding of:

- Building maintainable data-processing workflows.
- Working with inconsistent real-world datasets.
- Using relational databases to organize research metadata.
- Designing data validation into processing pipelines.
- Implementing algorithms for anomaly detection and record reconciliation.
- Developing interactive tools for technical users.
- Integrating multiple software components to address research requirements.

It also reinforced the importance of understanding user workflows and validating system outputs before relying on automated results.

---

## Repository and Data Availability

This repository serves as a technical portfolio and project case study.

The original research environment may contain institution-owned source code, experimental datasets, and internal materials that are not authorized for public distribution.

Only information and materials approved for public sharing will be included.

Where practical, synthetic datasets, independent examples, or conceptual diagrams may be used to demonstrate engineering approaches without disclosing restricted research information.

---

## Project Information

**Institution:** Arizona State University

**Research Center:** Arizona Center for Algae Technology and Innovation (AzCATI)

**Role:** Graduate Research Assistant — Data Engineering

**Field:** Software Engineering, Data Engineering, Research Automation

**Project Status:** Ongoing development

---

## About the Developer

**Maryam Younan**

M.S. Software Engineering — Arizona State University

B.S. Robotics Engineering

Interests include software engineering, data engineering, intelligent automation, full-stack applications, and practical AI systems.

**GitHub:** https://github.com/MaryamYounan18

---

*This repository documents individual engineering contributions within a broader university research project. It is not an official AzCATI software release or an endorsement by Arizona State University.*
