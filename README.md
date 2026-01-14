# FAO FDI Analysis – World Bank Open Data

## 📌 Project Overview

This project presents an **end‑to‑end data science workflow** using **Foreign Direct Investment (FDI) inflows to Agriculture, Forestry, and Fishing**, sourced from **World Bank Open Data (FAO indicators)**.

The purpose of this repository is to **demonstrate practical data science skills**—from data cleaning and exploratory data analysis (EDA) to visualisation, basic machine learning, and insight generation—using a real‑world public dataset.

This project is intentionally designed to be **clear, interpretable, and recruiter‑friendly**, making it suitable for a **junior data science / Python portfolio**.

---

## 📊 Data Source

* **Provider**: World Bank Open Data
* **Dataset**: FAO – FDI inflows to Agriculture, Forestry and Fishing
* **Frequency**: Annual
* **Coverage**: Multiple countries and years
* **Unit of Measurement**: Millions (USD)

The raw dataset is provided as a CSV file and includes both **metadata** and **observational values**.

---

## 🛠 Tools & Libraries Used

* **Python**
* **pandas** – data loading, cleaning, and transformation
* **NumPy** – numerical operations
* **Matplotlib / Seaborn** – data visualisation
* **scikit‑learn** – machine learning (linear regression)

---

## 🔍 Project Workflow

### 1. Data Loading

* Imported the CSV file using `pandas.read_csv()`
* Inspected the dataset structure using `.head()`, `.info()`, and `.describe()`

**Goal:** Understand column structure, data types, and data quality.

---

### 2. Data Cleaning & Preparation

**Actions taken:**

* Selected only relevant columns:

  * Country name
  * Year
  * FDI inflow value
* Renamed columns for clarity
* Converted year and FDI values to numeric types
* Removed missing and invalid records

**Reasoning:**
The original dataset contains extensive metadata. Reducing it to essential analytical fields improves clarity, performance, and interpretability.

---

### 3. Exploratory Data Analysis (EDA)

EDA was conducted to understand overall trends, distributions, and country‑level patterns.

**Key EDA steps:**

* Aggregated global FDI inflows by year
* Identified top countries by total FDI received
* Examined individual country trends over time

**Purpose:**

* Detect long‑term trends
* Identify dominant contributors
* Understand variation across countries

---

### 4. Data Visualisation

The project includes **2–3 clear, eye‑catching visualisations**:

1. **Global FDI Trend Over Time**

   * Line chart showing total global FDI inflows per year

2. **Top 10 Countries by Total FDI**

   * Bar chart highlighting countries with the highest cumulative inflows

3. **Country‑Level Trend Analysis**

   * Line chart illustrating FDI changes for a selected country

**Design focus:**

* Clean layout
* Clear axis labels
* Readable titles
* Portfolio‑appropriate visuals

---

### 5. Insight Generation

From the analysis, several insights emerged:

* Global agricultural FDI shows **cyclical patterns**, often influenced by global economic conditions
* A small number of countries receive a **disproportionate share** of total inflows
* Country‑specific trends vary significantly, reflecting differences in policy, economic stability, and investment climate

---

### 6. Machine Learning Application

A **simple linear regression model** was implemented to demonstrate a basic ML workflow.

**Method:**

* Selected one country as a case study
* Used **Year** as the independent variable
* Predicted **FDI inflows** as the target variable

**Steps:**

* Train/test split
* Model training using `LinearRegression`
* Evaluation using Mean Squared Error (MSE) and R² score

**Note:**
This model is **illustrative**, not predictive. Economic time‑series data typically require more advanced techniques.

---

## ⚠️ Limitations

* FDI is influenced by many external factors (policy, GDP, geopolitics) not included in the dataset
* Linear regression oversimplifies temporal dynamics
* Missing macroeconomic indicators limit explanatory power

---

## ✅ Conclusion

This project demonstrates the ability to:

* Work with real‑world public datasets
* Clean and structure complex data
* Perform exploratory and visual analysis
* Apply basic machine learning techniques
* Communicate insights clearly and professionally

It is designed to showcase **core data science competencies** in a concise and reproducible manner.

---

## 🚀 Future Improvements

* Integrate macroeconomic indicators (GDP, inflation)
* Apply time‑series models (ARIMA, Prophet)
* Add interactive visualisations (Plotly)
* Build a lightweight Streamlit dashboard

---

## 📁 Repository Structure (Suggested)

```
├── data/
│   └── FAO_FDI.csv
├── notebooks/
│   └── fdi_analysis.ipynb
├── README.md
```

---

## 📬 Contact

For questions, feedback, or collaboration, feel free to connect via GitHub.
