# 🧠 Student Mental Health Score Prediction

> **Machine Learning project to analyze student lifestyle and digital-usage patterns and predict a continuous mental health score.**

[![Python](https://img.shields.io/badge/Python-3.x-38BDF8?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-334155?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Scikit--learn](https://img.shields.io/badge/Scikit--learn-Machine%20Learning-38BDF8?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebooks-334155?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org/)

---

## 📌 Project Overview

Students' mental well-being can be influenced by multiple lifestyle and digital-usage factors such as social-media/platform usage, study time, physical activity, sleep, and stress.

This project follows an end-to-end **Data Science + Machine Learning workflow** to understand these patterns and build a regression model that predicts a student's **Mental Health Score**.

The project is currently **in progress**. The data analysis and baseline model development are completed, while hyperparameter tuning and the final predictor are still being developed.

---

## 🎯 Problem Statement

The goal is to investigate whether student lifestyle and digital-usage variables can be used to predict a continuous **Mental Health Score** using machine learning regression techniques.

### Objectives

- Understand the structure and quality of the dataset.
- Clean and prepare the data for analysis.
- Explore relationships between student habits and mental health score.
- Engineer and transform features for machine learning.
- Compare regression models.
- Identify a strong baseline model.
- Tune the selected model to improve its performance.
- Build a reliable final prediction workflow.

> ⚠️ **Important:** This project is an academic machine-learning project. The predicted score is **not a medical diagnosis or a substitute for professional mental-health assessment.**

---

## 📊 Dataset

The original dataset contains **5,000 student records and 13 columns**.

After data cleaning, **2 duplicate records were removed**, leaving **4,998 records** for further analysis.

### Key Features

| Category | Features |
|---|---|
| Demographics | Age, Gender, Country, Academic Level |
| Digital Usage | Most Used Platform, Purpose of Use, Average Daily Usage Hours, Daily Unlocks |
| Lifestyle | Study Hours, Physical Activity Hours, Sleep Hours per Night |
| Well-being | Stress Level |
| Target | Mental Health Score |

### Target Variable

**`Mental_Health_Score`** — a continuous numerical value used as the prediction target, making this a **regression problem**.

---

## 🔄 Data Science Workflow

```text
Raw Dataset
     ↓
Data Understanding
     ↓
Data Cleaning
     ↓
Exploratory Data Analysis (EDA)
     ↓
Feature Engineering
     ↓
Model Building
     ↓
Hyperparameter Tuning
     ↓
Final Predictor
```

The workflow is divided into separate notebooks so that each stage of the project can be understood and reproduced independently.

---

## 📓 Project Notebooks

### 01 — Data Understanding

`Notebooks/01_Data_Understanding.ipynb`

- Inspected dataset structure and dimensions.
- Examined columns and data types.
- Reviewed descriptive statistics.
- Identified the variables required for further analysis.

### 02 — Data Cleaning

`Notebooks/02_Data_Cleaning.ipynb`

- Checked data quality.
- Checked for missing values.
- Identified duplicate records.
- Removed **2 duplicate rows**.
- Prepared the cleaned dataset for EDA.

### 03 — Exploratory Data Analysis

`Notebooks/03_EDA.ipynb`

The EDA stage includes:

- Univariate analysis.
- Bivariate analysis.
- Correlation analysis.
- Correlation heatmap.
- Target-variable distribution analysis.
- Visualization of important relationships and patterns.

EDA visualizations are organized under the `Images/` directory.

### 04 — Feature Engineering

`Notebooks/04_Feature_Engineering.ipynb`

The feature-engineering pipeline separates the predictors into categorical and numerical features.

**Categorical features:**

- Gender
- Country
- Academic Level
- Most Used Platform
- Purpose of Use
- Stress Level

**Numerical features:**

- Age
- Average Daily Usage Hours
- Daily Unlocks
- Study Hours
- Physical Activity Hours
- Sleep Hours per Night

The notebook uses:

- `OneHotEncoder`
- `OrdinalEncoder`
- `StandardScaler`
- `ColumnTransformer`

The processed feature dataset contains **4,998 rows and 77 columns** after transformation.

### 05 — Model Building

`Notebooks/05_Model_Building.ipynb`

Multiple regression models were evaluated to identify a strong baseline model for predicting `Mental_Health_Score`.

### 06 — Model Tuning

`Notebooks/06_Model_Tunning.ipynb`

The current tuning workflow uses **RandomizedSearchCV** with a `RandomForestRegressor`.

Configuration currently defined in the notebook:

- 20 randomized parameter combinations.
- 5-fold cross-validation.
- `r2` scoring.
- `random_state = 42`.
- `n_jobs = -1`.
- Parameters considered include `n_estimators`, `max_depth`, `min_samples_split`, `min_samples_leaf`, and `max_features`.

> 🚧 **Current status:** The hyperparameter-tuning notebook is still being completed. Therefore, a final tuned-model score is intentionally **not claimed here**.

---

## 📈 Current Model Status

Among the regression models evaluated so far, **Random Forest Regression** produced the strongest baseline result recorded in the project.

**Baseline R² Score: `0.9167`**

This is the current baseline result, **not the final tuned-model performance**.

| Stage | Model / Method | Status | Result |
|---|---|---|---:|
| Baseline comparison | Multiple regression models | ✅ Completed | — |
| Best baseline | Random Forest Regressor | ✅ Completed | **R² = 0.9167** |
| Hyperparameter tuning | RandomizedSearchCV | 🚧 In progress | Not finalized |
| Final predictor | Final tuned pipeline | ⏳ Planned | Not available yet |

---

## 🖼️ Visualizations

The repository contains dedicated folders for the project's analysis visuals:

```text
Images/
├── 01_Univariate_Analysis_Plots_Images/
├── 02_Bivariate_Analysis_Plots_Images/
├── 03_Correlation_Heatmap_Image/
└── 04_Target_Variable_Analysis_Image/
```

These visualizations support the exploratory analysis and help communicate relationships within the dataset.

---

## 🗂️ Repository Structure

```text
Students_Mental_Health_Score_Prediction_sys/
│
├── Data/
│   ├── 01_Raw/
│   ├── 02_Cleaned/
│   └── 03_Processed/
│
├── Images/
│   ├── 01_Univariate_Analysis_Plots_Images/
│   ├── 02_Bivariate_Analysis_Plots_Images/
│   ├── 03_Correlation_Heatmap_Image/
│   └── 04_Target_Variable_Analysis_Image/
│
├── Notebooks/
│   ├── 01_Data_Understanding.ipynb
│   ├── 02_Data_Cleaning.ipynb
│   ├── 03_EDA.ipynb
│   ├── 04_Feature_Engineering.ipynb
│   ├── 05_Model_Building.ipynb
│   ├── 06_Model_Tunning.ipynb
│   └── Mental_Health_Predictor.ipynb
│
├── Synopsis_and_Reports/
│   └── 01_Synopsis/
│
├── README.md
└── requirement.txt
```

---

## 🛠️ Tech Stack

- **Python** — core programming language
- **Pandas** — data manipulation and analysis
- **NumPy** — numerical operations
- **Matplotlib** — data visualization
- **Seaborn** — statistical visualization
- **Scikit-learn** — preprocessing, regression, model evaluation and tuning
- **Jupyter Notebook** — interactive development and documentation

---

## ▶️ How to Explore the Project

Clone the repository and open the notebooks in the following order:

```text
01_Data_Understanding
        ↓
02_Data_Cleaning
        ↓
03_EDA
        ↓
04_Feature_Engineering
        ↓
05_Model_Building
        ↓
06_Model_Tunning
```

The project is structured so that the complete workflow can be followed from raw data preparation through model development.

> **Note:** The `requirement.txt` file is currently being prepared as the project continues to evolve.

---

## 🚧 Current Project Status

**Status: In Progress**

### Completed

- [x] Data understanding
- [x] Data cleaning
- [x] Exploratory data analysis
- [x] Feature engineering
- [x] Baseline model comparison
- [x] Identification of the strongest baseline model

### In Progress

- [ ] Complete hyperparameter tuning
- [ ] Evaluate the tuned Random Forest model
- [ ] Finalize the prediction pipeline
- [ ] Complete the final predictor notebook
- [ ] Finalize project dependencies

---

## 🔮 Planned Improvements

- Complete and evaluate hyperparameter tuning.
- Compare tuned performance against the current baseline.
- Finalize a reproducible prediction pipeline.
- Add final model evaluation metrics once available.
- Add a simple prediction interface after the model is finalized.
- Improve documentation with final model insights and limitations.

---

## 📚 What This Project Demonstrates

This project demonstrates practical experience with an end-to-end machine-learning workflow, including:

- Data understanding and quality checking.
- Data cleaning and duplicate handling.
- Exploratory data analysis.
- Categorical encoding and numerical scaling.
- Feature transformation using `ColumnTransformer`.
- Regression model comparison.
- Cross-validation and hyperparameter-search concepts.
- Model evaluation using R².
- Organizing a data-science project into reproducible stages.

---

## 👩‍💻 Author

**Rutuja Dhumal**  
B.Sc. Data Science Student | Aspiring Data Scientist & Data Analyst

- GitHub: [@rutuu0228](https://github.com/rutuu0228)
- LinkedIn: [rutuu0208](https://www.linkedin.com/in/rutuu0208/)

---

## ⭐ Project Note

This repository is being developed as a practical Data Science and Machine Learning project. The documentation will continue to evolve as model tuning, final evaluation, and the prediction workflow are completed.

If you find the project useful, consider giving it a ⭐ on GitHub.
