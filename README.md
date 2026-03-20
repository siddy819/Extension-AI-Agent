# 📊 Extension Impact Narrative Agent

Transform your raw Extension data into professional impact narratives and visual dashboards. This application provides a multi-agent AI pipeline designed to automate the heavy lifting of county-level reporting for Extension professionals.

## ✨ Features
*   **Dynamic Impact Dashboard**: Readily visualize KPIs like Total Contacts, Knowledge Gain, and Delivery Methods via interactive Plotly charts.
*   **Intelligent Filtering**: Slice your data seamlessly by subsets (e.g., County or Topic) to calculate hyper-specific insights. 
*   **Multi-Model LangChain AI Pipeline**:
    *   **Agent 1 (Narrative Engine):** Automatically processes filtered statistical metrics and qualitative feedback into a comprehensive, written UF/IFAS-standard impact report.
    *   **Agent 2 (Interactive Q&A):** A context-aware chatbot grounded exclusively in your dataset, ready to answer questions, write emails, or pull specific insights on demand. 
*   **1-Click Comprehensive PDF Export**: Generates a perfectly formatted PDF spanning your dashboard visualizations, the structured core narrative, and the full interactive Q&A history.

---

## 🚀 Getting Started

Follow these steps to set up and run the application locally.

### 1. Clone the Repository
Download the project to your local machine:
```bash
git clone https://github.com/siddy819/Extension-AI-Agent.git
cd Extension-AI-Agent
```

### 2. Set Up a Virtual Environment (Highly Recommended)
Creating a virtual environment ensures that the required packages don't conflict with other projects on your system.

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all the required Python libraries using the generated `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Boot up the Streamlit server:
```bash
streamlit run app.py
```
*The app should automatically open in your default web browser at `http://localhost:8501/`.*

---

## 🗂️ How to Use the App

1. **Provide API Credentials**: In the left sidebar, enter the secure API keys for Agent 1 and Agent 2 (powered via the UF IT enterprise endpoint).
2. **Upload Data**: Drag and drop the provided `mock_data.csv` file (or your own CSV data matching the exact schema) into the upload box.
3. **Filter & Explore**: Use the dropdown menus to refine which Counties or program Topics you want to analyze.
4. **Generate the Report**: Click **"🚀 Run Agent 1"** to watch the narrative stream onto the screen.
5. **Ask Follow-Ups**: Scroll down to Agent 2's chat bar to ask specific, grounded follow-up questions about the data subset. 
6. **Export**: Click the **"💾 Download Comprehensive Report (.pdf)"** button to save the entire end-to-end workflow to your hard drive. 

---

## 📝 Required Data Schema
If you use your own dataset, the uploaded CSV **must** contain exactly these headers:
`Program Date`, `County`, `Program Name`, `Topic`, `Total Contacts`, `Indirect Reach`, `Surveys Collected`, `Knowledge Gain (%)`, `Behavior Change (%)`, `Program Type`, `Target Audience`, `Success Story`, `Qualitative Feedback`
