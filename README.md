# ECG-Project-2026
This repository contains ECG and body movement data for analyzing the relationship between physical activity and cardiovascular health.

## Structure

- **InitialData/**  
  Contains the raw data collected during the first acquisition stage, before cleaning and renaming.

- **samples-renamed/**  
  Contains the final, cleaned, and organized dataset used for analysis.  
  The data is grouped by activity, using a numerical prefix followed by the activity name:

  - **1-sit/**: Sitting activity  
  - **2-stand/**: Standing activity  
  - **3-walk/**: Walking activity  
  - **4-jump/**: Jumping activity  
  - **5-run/**: Running activity  
  - **6-climbup/**: Climbing up stairs  
  - **7-climbdown/**: Climbing down stairs  

## Data
The data is organized by activity and subject, where "subject1", "subject2", etc., represent the different subjects in the study.

## Information about the subjects

| Subject | Age | Sex    | Weight (kg) | Height (m) | Cardiac/Pulmonary Disease | Smoker |
|---------|-----|--------|------------|------------|----------------------------|--------|
| S1      | 26  | Male   | 83         | 1.78       | None                       | Yes    |
| S2      | 23  | Female | 65         | 1.69       | None                       | No     |
| S3      | 19  | Male   | 96         | 1.85       | None                       | Yes    |
| S4      | 20  | Female | 62         | 1.69       | None                       | No     |
| S5      | 22  | Male   | 81         | 1.89       | None                       | No     |
| S6      | 20  | Female | 60         | 1.60       | None                       | Yes    |
| S7      | 24  | Male   | 70         | 1.88       | None                       | No     |
| S8      | 19  | Female | 58         | 1.73       | None                       | No     |
| S9      |     |        |            |            |                            | Yes    |
| S10     | 21  | Female | 68         | 1.71       | None                       | No     |
