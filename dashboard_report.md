# PV-CONNECT Dashboard & Analytics Module

## Overview
The PV-CONNECT Dashboard serves as the central command center for pharmacovigilance activities, providing real-time visibility into adverse event reporting, case processing status, and advanced signal detection analytics. It is designed to empower safety officers with data-driven insights for timely decision-making.

## Key Features

### 1. comprehensive Case Management Metrics
The dashboard provides an immediate high-level summary of the entire safety database:
- **Case Volume Tracking**: Real-time counters for "Total Cases", providing a snapshot of the database size.
- **Workflow Status**: Dedicated metrics for "Pending Review", "Completed", and "Escalated" cases, allowing managers to track workload and identify bottlenecks in the processing pipeline.

### 2. Interactive Data Visualization
To facilitate intuitive data exploration, the dashboard features a suite of interactive charts:
- **Severity Distribution**: A bar chart visualizing the breakdown of cases by severity (Severe, Moderate, Mild), helping teams prioritize high-impact safety issues.
- **Processing Status**: A pie chart offering a visual representation of case statuses, useful for monitoring team progress and compliance.
- **Top Suspect Drugs**: A ranked horizontal bar chart identifying the top 5 drugs associated with adverse events, enabling quick identification of problematic products.
- **Confidence Score Distribution**: An area chart displaying the distribution of VigiGrade completeness scores, providing insight into the overall quality of the reported data.

### 3. Advanced Signal Detection (FAERS Integration)
A specialized module integrates external data from the FDA Adverse Event Reporting System (FAERS) to perform advanced signal detection using the **BCPNN (Bayesian Confidence Propagation Neural Network)** algorithm.

- **Automated Analysis**: The system automatically ingests FAERS data and processes it to calculate Information Components (IC) for Drug-Event pairs.
- **Signal Strength Classification**: detected signals are classified and color-coded based on their IC Lower Bound (IC025):
  - **Very Strong** (Red): IC > 3.0
  - **Strong** (Yellow): IC > 1.0
  - **Moderate** (Blue): IC > 0.0
- **Detailed Reporting Table**: A granular table displays specific findings, including:
  - **Suspect Product & Adverse Event**: The specific pair being analyzed.
  - **Observed vs. Expected**: Comparing actual report counts against statistical expectations.
  - **IC Score**: The precise Bayesian information component score.
  - **Signal Strength indicator**: Visual badge for quick risk assessment.

## Technical Implementation
- **Frontend**: Built with React and Recharts for responsive, high-performance visualization.
- **Backend**: Powered by FastAPI and MongoDB for efficient data aggregation.
- **Algorithm**: Implements the WHO-UMC standard BCPNN algorithm for robust duplicate detection and signal refinement.
