# Banking Fraud Detection Using Data Mining and Machine Learning
**A Production-Grade Intelligent Financial Crime Surveillance & Risk Classification System**

---

## 1. ABSTRACT
Financial fraud in modern electronic banking ecosystems inflicts billions of dollars in global annual losses, undermining consumer confidence and financial institution stability. Detecting unauthorized credit card and electronic transactions in real time poses acute challenges due to extreme class imbalance (less than 0.2% fraudulent transactions), high transaction throughput, dynamic fraudster evasion techniques, and stringent latency budgets. This project presents an end-to-end, industry-standard banking fraud detection and surveillance application termed **Sentinel Fraud Intelligence**. Leveraging data mining and machine learning, the system ingests 284,807 European cardholder transactions, rigorously trains and benchmarks five distinct algorithms—Logistic Regression, Decision Trees, Random Forest, Support Vector Machines (Linear SVC with probability calibration), and Isolation Forest—and deploys the optimal Random Forest ensemble achieving an **F1-Score of 0.7793**, **Fraud Recall of 84.69%**, and **PR-AUC of 0.8256**. The architecture incorporates an explainable AI feature attribution engine, a Flask application service layer with SQLAlchemy ORM and SQLite, administrative audit logging, and a modern responsive dashboard built with Bootstrap 5 and Chart.js.

---

## 2. INTRODUCTION
Digital transformation in consumer and corporate banking has catalyzed electronic fund transfers, point-of-sale (POS) authorizations, and e-commerce payments. Concurrently, cybercriminals exploit sophisticated vectors such as credential stuffing, automated card testing bots, identity theft, and synthetic identity schemes. Traditional fraud detection systems in banking relied heavily on static rule-based engines (e.g., flagging single transactions exceeding \$5,000 or international geographic jumps). While effective against primitive anomalies, static heuristics produce excessive false positives, degrade customer experience, and fail against nuanced behavioral compromises.

Machine learning and data mining transform fraud defense from reactive rules to adaptive predictive intelligence. By analyzing multi-dimensional behavioral signatures, statistical deviations, and feature interactions across millions of historical transactions, modern models uncover latent non-linear indicators of compromise in sub-second intervals.

---

## 3. PROBLEM STATEMENT
Financial fraud detection is characterized by three core machine learning hurdles:
1. **Extreme Class Imbalance:** Legitimate transactions comprise over 99.8% of daily banking volume, while fraudulent records constitute fewer than 0.2%. Conventional classifiers optimizing naive accuracy converge on majority-class classification (predicting all records as legitimate), resulting in fatal false negatives.
2. **Asymmetric Misclassification Costs:** In financial institutions, a False Negative (failing to stop a \$2,500 fraudulent wire) is substantially costlier than a False Positive (prompting a legitimate customer for two-factor authentication).
3. **Black-Box Opacity vs. Regulatory Compliance:** Financial compliance standards (e.g., PCI-DSS, GDPR, FCRA) mandate that automated credit decisions and transaction holds provide explainable indicators justifying the security action.

---

## 4. EXISTING SYSTEM
Traditional commercial banking architectures employ rule-based fraud detection engines:
- Hardcoded conditional logic (e.g., `IF amount > limit AND country != home THEN flag`).
- Batch post-processing queries running overnight across data warehouses.
- Manual verification queues staffed by human fraud analysts with hours of delay.

### Limitations of Existing Systems:
- **Zero Adaptation:** Inability to detect zero-day fraud patterns without manual rule writing.
- **High Maintenance Overhead:** Rule databases quickly balloon into thousands of contradictory conditions.
- **Elevated False Alarm Rates:** Innocent customers face card declines at merchant checkouts.
- **Latency Lag:** Fraudulent funds are withdrawn long before overnight batch jobs flag the account.

---

## 5. PROPOSED SYSTEM
The proposed **Sentinel Banking Fraud Detection System** integrates statistical data mining, machine learning pipelines, and real-time web surveillance:
- **Stratified Robust Preprocessing:** Handles numerical feature outliers without data leakage across training and test splits.
- **Empirical Multi-Model Benchmarking:** Evaluates five diverse learning paradigms (linear, tree-based, ensemble, kernel-based, and unsupervised anomaly detection).
- **Metric-Driven Selection:** Selects models using Precision-Recall Area Under Curve (PR-AUC) and F1-score rather than deceiving accuracy metrics.
- **Explainable Diagnostic Attribution:** Generates human-interpretable Z-score indicators explaining *why* a transaction was assigned a high risk score.
- **Real-Time Surveillance Dashboard:** Provides administrators with live transaction simulation, KPI monitoring, interactive Chart.js visualizations, CSV batch processing, and audit logs.

---

## 6. OBJECTIVES
1. Develop an intelligent machine learning pipeline capable of sub-millisecond fraud probability scoring.
2. Mitigate severe class imbalance through balanced class weighting and robust feature scaling.
3. Benchmark Logistic Regression, Decision Tree, Random Forest, Calibrated SVM, and Isolation Forest on genuine credit card transaction data.
4. Establish a multi-tiered risk taxonomy: Low (<20%), Medium (20–50%), High (50–80%), and Critical (≥80%).
5. Build an intuitive web-based administrative console with real-time transaction streaming, CSV bulk upload, and filterable history.
6. Provide explainable AI risk indicators attributing primary anomaly drivers for each flagged event.
7. Maintain immutable audit trails of all administrative investigation actions.

---

## 7. SCOPE OF THE PROJECT
- **Functional Scope:** Ingestion of single manual transactions, bulk CSV file uploads (up to 5,000 rows/batch), real-time transaction simulation, database persistence, analytical dashboards, CSV report generation, and case investigation status management.
- **Algorithmic Scope:** Supervised classification and unsupervised outlier identification on 30 principal component and numerical attributes.
- **Security Scope:** Session authentication, password hashing (PBKDF2/SHA-256), input validation, file upload whitelisting, and SQL injection prevention via SQLAlchemy ORM.

---

## 8. LITERATURE SURVEY
1. **Dal Pozzolo et al. (2015):** Studied credit card fraud detection on 284,807 transactions. Emphasized that concept drift and extreme imbalance mandate non-standard metrics such as PR-AUC and Average Precision.
2. **Carminati et al. (2018):** Demonstrated that ensemble decision tree methods (Random Forests and Gradient Boosters) consistently outperform single neural networks on tabular financial data with sparse positive samples.
3. **Liu, Ting, and Zhou (2008):** Introduced Isolation Forests for anomaly detection, illustrating that anomalies are "few and different" and therefore isolated closer to tree roots in random partitioning trees.
4. **Chawla et al. (2002):** Proposed SMOTE (Synthetic Minority Over-sampling Technique). Highlighted that oversampling must strictly reside inside cross-validation training folds to avert artificial performance inflation.

---

## 9. SYSTEM REQUIREMENTS

### Hardware Requirements
- **Processor:** 64-bit multi-core CPU (Intel Core i5 / AMD Ryzen 5 or higher).
- **RAM:** Minimum 8 GB (16 GB recommended for parallel ensemble fitting).
- **Disk Space:** 2 GB available storage (to accommodate the 150MB CSV dataset, trained artifacts, and database).

### Software Requirements
- **Operating System:** Windows 10/11, macOS Monterey+, or Ubuntu Linux 22.04 LTS.
- **Runtime Environment:** Python 3.9 through 3.15 (64-bit).
- **Backend Framework:** Flask 3.1+, Flask-SQLAlchemy 3.1+, Werkzeug 3.1+.
- **Data Science Stack:** Scikit-Learn 1.3+, Pandas 2.0+, NumPy 1.24+, Matplotlib 3.7+, Seaborn 0.12+.
- **Frontend Assets:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Chart.js 4.4, FontAwesome 6.4.

---

## 10. SYSTEM ARCHITECTURE

```
+---------------------------------------------------------------------------------------+
|                                    CLIENT BROWSER                                     |
|  - HTML5 / Bootstrap 5 / Chart.js Interactive Dashboards                              |
|  - Single Transaction Input, CSV Batch Uploader, Real-Time Transaction Simulator     |
+---------------------------------------------------------------------------------------+
                                           |  HTTPS / JSON Requests
                                           v
+---------------------------------------------------------------------------------------+
|                                   FLASK SERVICE LAYER                                 |
|  - routes/auth.py         : Administrator Authentication, PBKDF2 Password Checks      |
|  - routes/dashboard.py    : Real-Time Analytics, Chart Data Endpoints, Sim Engine    |
|  - routes/transactions.py : Single & Bulk Batch Prediction, History & Investigation   |
|  - routes/reports.py      : Audit Trail Reports, CSV Export Generator                 |
+---------------------------------------------------------------------------------------+
                     |                                           |
                     v                                           v
+-----------------------------------------+   +-----------------------------------------+
|        DATABASE & PERSISTENCE           |   |       PREPROCESSING & ML ENGINE         |
|  - database/db.py (SQLAlchemy ORM)      |   |  - RobustScaler (Amount, Time)          |
|  - SQLite (banking_fraud.db)            |   |  - Deployed Random Forest (.pkl)        |
|  - Tables: User, Transaction, AuditLog  |   |  - Explainable Feature Factor Analysis  |
+-----------------------------------------+   +-----------------------------------------+
```

---

## 11. DATA FLOW DIAGRAMS

### Data Flow Diagram - Level 0 (Context Diagram)
```
[ Administrator / Analyst ] 
            |
            | (1) Transaction Details / CSV Batch
            v
+===================================================+
|                                                   |
|   BANKING FRAUD DETECTION SYSTEM (SENTINEL)       |
|                                                   |
+===================================================+
            |
            | (2) Fraud Probability, Risk Level, Anomaly Reasons, Charts
            v
[ Administrator / Analyst ]
```

### Data Flow Diagram - Level 1
```
[ User Input / CSV ] 
        |
        v
[ 1.0 Input Validation & Sanitization ] 
        |
        v
[ 2.0 Robust Feature Scaling ] <---> [ Fitted Scalers (scaler.pkl) ]
        |
        v
[ 3.0 ML Model Inference ] <-------- [ Random Forest (fraud_model.pkl) ]
        |
        v (Probability)
[ 4.0 Risk Classifier & Indicator Attribution ]
        |
        v
[ 5.0 Database Persistence ] <------> [ SQLite Database (banking_fraud.db) ]
        |
        v
[ 6.0 UI Dashboard & Visualizations ]
```

---

## 12. USE CASE DIAGRAM
```
                       +---------------------------------------------------+
                       |              BANKING FRAUD SYSTEM                 |
                       |                                                   |
                       |   ( Administrator Authentication / Login )        |
                       |                     ^                             |
                       |                     |                             |
                       |   ( View Real-Time Executive Dashboard )          |
                       |                     ^                             |
                       |                     |                             |
    (( Administrator ))|---( Execute Single Transaction Fraud Analysis )   |
                       |                     |                             |
                       |   ( Ingest & Classify Bulk CSV Batches )          |
                       |                     |                             |
                       |   ( Trigger Simulated Live Transactions )         |
                       |                     |                             |
                       |   ( Filter & Search Transaction History )         |
                       |                     |                             |
                       |   ( Investigate & Annotate Suspicious Events )    |
                       |                     |                             |
                       |   ( Compare Machine Learning Algorithm Metrics )  |
                       |                     |                             |
                       |   ( Export Transaction Audit Reports to CSV )     |
                       +---------------------------------------------------+
```

---

## 13. ENTITY-RELATIONSHIP (ER) DIAGRAM
```
+---------------------------+             +---------------------------+
|          USERS            |             |        AUDIT_LOGS         |
+---------------------------+             +---------------------------+
| id (PK, Integer)          |1           *| id (PK, Integer)          |
| username (String, Unique) |-------------| user_id (FK -> users.id)  |
| password_hash (String)    |             | username (String)         |
| role (String)             |             | action (String)           |
| created_at (DateTime)     |             | ip_address (String)       |
| last_login (DateTime)     |             | details (Text)            |
+---------------------------+             | timestamp (DateTime)      |
                                          +---------------------------+

+-----------------------------------------+
|              TRANSACTIONS               |
+-----------------------------------------+
| id (PK, Integer)                        |
| transaction_id (String, Unique, Index)  |
| time_offset (Float)                     |
| amount (Float)                          |
| feature_v1 .. feature_v28 (Float)       |
| prediction (String: Legit/Fraud)        |
| is_fraud (Boolean)                      |
| fraud_probability (Float)               |
| risk_level (String: Low/Med/High/Crit)  |
| indicators_json (Text)                  |
| is_investigated (Boolean)               |
| investigation_status (String)           |
| admin_notes (Text)                      |
| created_at (DateTime, Index)            |
+-----------------------------------------+
```

---

## 14. METHODOLOGY
The system follows an engineering methodology divided into 6 distinct stages:
1. **Data Ingestion & Hygiene:** Loaded 284,807 transaction rows. Cleaned 0 null entries, tracked 1,081 duplicate records, verified numerical types.
2. **Leak-Free Partitioning:** Stratified splitting ensures identical minority class ratios (0.17%) in train (227,845 rows, 394 frauds) and test (56,962 rows, 98 frauds) partitions.
3. **Robust Scaling:** Transformed `Amount` and `Time` using median and interquartile ranges via `RobustScaler`, neutralizing extreme outlier distortion.
4. **Multi-Model Empirical Training:** Fit 5 algorithms using balanced class penalties.
5. **Model Serialization:** Persisted preprocessor and champion Random Forest weights.
6. **Full-Stack Deployment:** Integrated REST endpoints with responsive presentation templates.

---

## 15. DATA MINING TECHNIQUES
- **Dimensionality Reduction (PCA):** Analyzed 28 orthogonal principal components ($V_1$ through $V_{28}$) preserving sensitive financial behavioral variance while ensuring customer privacy.
- **Statistical Correlation Mining:** Computed Pearson correlation against target `Class`. Discovered significant negative drivers:
  - $V_{14}$ ($r = -0.3025$)
  - $V_{12}$ ($r = -0.2606$)
  - $V_{10}$ ($r = -0.2169$)
  - $V_{17}$ ($r = -0.3265$)
  And key positive drivers:
  - $V_4$ ($r = +0.1334$)
  - $V_{11}$ ($r = +0.1549$)
- **Anomaly Detection Mining:** Modeled spatial isolation metrics using random recursive hyperplanes (Isolation Forest) to isolate unsupervised spatial outliers.

---

## 16. MACHINE LEARNING ALGORITHMS

### 1. Logistic Regression
Models the log-odds of a transaction being fraudulent as a linear combination of features:
$$\log\left(\frac{P(Y=1|X)}{1 - P(Y=1|X)}\right) = \beta_0 + \sum_{i=1}^{30} \beta_i X_i$$
To counteract class imbalance, we applied balanced class weights:
$$w_c = \frac{N}{2 \times N_c}$$

### 2. Decision Tree Classifier
Recursively partitions feature space using Gini impurity:
$$I_G(t) = 1 - \sum_{i=0}^{1} p_i^2$$
Configured with maximum depth limits (`max_depth=8`) and minimum sample splits to prevent overfitting on rare fraud leaves.

### 3. Random Forest (Champion Model)
An ensemble of 100 decorrelated decision trees using bootstrap aggregating (bagging) and random feature subspace sampling:
$$\hat{P}(Y=1|X) = \frac{1}{B} \sum_{b=1}^{B} T_b(X)$$
By averaging probabilities across independent trees, variance is reduced while capturing complex non-linear feature interactions.

### 4. Support Vector Machine (Linear SVC + Calibrated Probability)
Constructs an optimal maximum-margin hyperplane:
$$\min_{w, b, \xi} \frac{1}{2} \|w\|^2 + C \sum_{i=1}^{n} w_{y_i} \xi_i$$
Calibrated using Platt Scaling / 3-fold cross-validation to transform raw decision distance into well-calibrated fraud probabilities.

### 5. Isolation Forest (Unsupervised Anomaly Detection)
Isolates anomalous instances by randomly partitioning feature space. Anomalies require fewer recursive splits to be isolated:
$$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
Where $E(h(x))$ is the average path length across 100 isolation trees.

---

## 17. IMPLEMENTATION DETAILS
- [`config.py`](file:///C:/Users/amogh/Downloads/banking-fraud-detection/config.py): Global configuration, paths, risk thresholds, and security parameters.
- [`preprocessing/data_preprocessing.py`](file:///C:/Users/amogh/Downloads/banking-fraud-detection/preprocessing/data_preprocessing.py): Leak-free `DataPreprocessor` class, single/batch transformations, and Z-score explainability attribution.
- [`models/train_model.py`](file:///C:/Users/amogh/Downloads/banking-fraud-detection/models/train_model.py): End-to-end model training, comparative benchmark evaluation, and ROC/PR curve plotting.
- [`database/db.py`](file:///C:/Users/amogh/Downloads/banking-fraud-detection/database/db.py): SQLAlchemy models (`User`, `TransactionRecord`, `AuditLog`).
- [`routes/auth.py`](file:///C:/Users/amogh/Downloads/banking-fraud-detection/routes/auth.py): Authentication, PBKDF2 hashing, and session management.
- [`routes/dashboard.py`](file:///C:/Users/amogh/Downloads/banking-fraud-detection/routes/dashboard.py): KPI aggregations, Chart.js APIs, and real-time transaction simulator.
- [`routes/transactions.py`](file:///C:/Users/amogh/Downloads/banking-fraud-detection/routes/transactions.py): Manual evaluation, bulk CSV ingestion, filterable history, and investigation workflows.
- [`routes/reports.py`](file:///C:/Users/amogh/Downloads/banking-fraud-detection/routes/reports.py): Executive reports, downloadable CSV log export, and performance comparison view.
- [`app.py`](file:///C:/Users/amogh/Downloads/banking-fraud-detection/app.py): Flask application factory, database initialization, and database seeding.

---

## 18. TESTING AND VALIDATION
Comprehensive automated unit and integration tests are codified in [`tests/test_app.py`](file:///C:/Users/amogh/Downloads/banking-fraud-detection/tests/test_app.py):
1. `test_login_success`: Validates admin authentication and session issuance.
2. `test_login_invalid_password`: Validates rejection of illegitimate credentials.
3. `test_protected_routes_redirect`: Confirms unauthenticated access to `/dashboard`, `/transactions`, etc. is blocked (HTTP 302 redirect to `/login`).
4. `test_dashboard_api`: Verifies dynamic JSON payload structure for Chart.js.
5. `test_predict_single_legitimate`: Tests manual evaluation with baseline values; verifies correct "Legitimate" classification (prob < 0.20).
6. `test_predict_single_fraudulent`: Tests manual evaluation with severe anomaly values (V14 = -9.5); verifies "Fraudulent" classification (prob > 0.80).
7. `test_bulk_csv_upload`: Validates batch parsing, feature alignment, and bulk database insert.
8. `test_invalid_file_upload_rejected`: Validates file extension security against non-CSV payloads.
9. `test_export_csv_report`: Validates dynamic generation of compliant RFC 4180 CSV export files.
10. `test_investigation_update`: Validates analyst status updates ("Confirmed Fraud") and note persistence.
11. `test_simulate_transaction_endpoint`: Tests real-time live simulation generation.

**All 11 tests execute in under 7 seconds with 100% pass rate.**

---

## 19. RESULTS AND DISCUSSION

### Algorithm Benchmark Comparison Table
*(Evaluated on Holdout Test Set: $N = 56,962$ transactions, Actual Frauds $= 98$)*

| Machine Learning Algorithm | Test Accuracy | Fraud Precision | Fraud Recall (Detection Rate) | F1-Score | ROC-AUC | PR-AUC | Training Duration |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest (Deployed)** | **99.92%** | **72.17%** | **84.69%** | **0.7793** | **0.9775** | **0.8256** | 22.80s |
| Support Vector Machine (Linear) | 99.90% | 80.28% | 58.16% | 0.6746 | 0.9742 | 0.7346 | 9.01s |
| Isolation Forest (Unsupervised) | 99.76% | 31.13% | 33.67% | 0.3235 | 0.9543 | 0.2180 | 2.37s |
| Decision Tree | 98.05% | 06.90% | 82.65% | 0.1274 | 0.9075 | 0.4749 | 8.11s |
| Logistic Regression | 97.55% | 06.09% | 91.84% | 0.1142 | 0.9720 | 0.7175 | 1.50s |

### Detailed Analysis:
- **Random Forest** achieved the highest overall discriminatory power (**PR-AUC of 0.8256** and **F1-Score of 0.7793**). It successfully detected 83 out of 98 real frauds with only 32 false positives across nearly 57,000 transactions.
- **Support Vector Machine** exhibited the highest precision (80.28%), but captured only 58.16% of fraudulent transactions.
- **Logistic Regression** achieved high recall (91.84%) but suffered from high false alarms (1,388 false positives), resulting in a poor precision of 6.09%.
- **Isolation Forest** demonstrated that unsupervised anomaly detection alone cannot match supervised ensembles when labeled fraud history is available.

---

## 20. ADVANTAGES AND LIMITATIONS

### Advantages:
1. **Industry-Grade Precision & Recall:** Minimizes costly false negatives without overwhelming fraud investigation teams with false alerts.
2. **Explainable AI Reasoning:** Every flagged transaction presents specific human-understandable drivers (e.g., Z-score anomalies in $V_{14}, V_{12}$, or transaction volume).
3. **Turnkey Operational Platform:** Includes interactive transaction simulator, CSV batch uploader, real-time Chart.js dashboard, and case investigation workflow.
4. **Data Leakage Immunity:** Preprocessing scalers are fitted strictly on training data folds.

### Limitations:
1. **Concept Drift:** Fraudsters continuously modify attack techniques over time, requiring periodic model retraining.
2. **Cold Start for New Merchants:** In absence of historical customer baseline parameters, behavioral profiling is less informative.

---

## 21. FUTURE ENHANCEMENTS
1. **Graph Neural Networks (GNNs):** Model money mule networks and synthetic identity rings by linking shared bank accounts, device IDs, and IP subnets.
2. **Deep Learning Sequence Models (LSTM / Transformers):** Ingest sequential cardholder transaction histories to detect anomalous velocity changes over time.
3. **Automated MLOps Pipeline:** Implement automated model retraining triggered by data drift thresholds.

---

## 22. CONCLUSION
The **Banking Fraud Detection Using Data Mining and Machine Learning** project successfully addresses the acute challenges of financial cybercrime surveillance. By combining rigorous leak-free preprocessing, class-weight adaptation, empirical benchmarking of 5 algorithms, and human-in-the-loop explainable AI, the system achieves industry-leading detection performance (**84.69% Recall, 0.7793 F1-Score, 0.8256 PR-AUC**). The resulting web application provides banking administrators with an end-to-end operational defense platform that unifies real-time transaction streaming, CSV bulk ingestion, automated risk scoring, and audit logging.

---

## 23. REFERENCES
1. Andrea Dal Pozzolo, Olivier Caelen, Reid A. Johnson, and Gianluca Bontempi. *Calibrating Probability with Undersampling for Unbalanced Classification.* IEEE Symposium on Computational Intelligence and Data Mining (CIDM), 2015.
2. Nitesh V. Chawla, Kevin W. Bowyer, Lawrence O. Hall, and W. Philip Kegelmeyer. *SMOTE: Synthetic Minority Over-sampling Technique.* Journal of Artificial Intelligence Research (JAIR), 16:321–357, 2002.
3. Fei Tony Liu, Kai Ming Ting, and Zhi-Hua Zhou. *Isolation Forest.* 8th IEEE International Conference on Data Mining, 413–422, 2008.
4. Leo Breiman. *Random Forests.* Machine Learning, 45(1):5–32, 2001.
5. Scikit-Learn Developers. *User Guide: Imbalanced Classification & Ensemble Methods.* Version 1.3+, 2024.
6. Kaggle & Machine Learning Group (ULB). *Credit Card Fraud Detection Dataset.* ULB Machine Learning Group, Brussels, Belgium.
