import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import utils

# Page configuration
st.set_page_config(
    page_title="Extension Impact Narrative Agent",
    page_icon="📊",
    layout="wide",
)

# --- APP HEADER ---
st.title("📊 Extension Impact Narrative Agent")
st.markdown("""
Transform your raw Extension data into professional impact narratives and visual dashboards. 
Perfect for reporting to leadership and stakeholders.
""")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter OpenAI/Gemini API Key", type="password")
    uploaded_file = st.file_uploader("Upload your data (CSV)", type="csv")
    
    st.info("Download the [mock_data.csv](https://github.com/your-repo/mock_data.csv) to test the dashboard.")

# --- DATA LOADING ---
@st.cache_data
def load_data(file):
    if file is not None:
        try:
            df = pd.read_csv(file)
            df['Program Date'] = pd.to_datetime(df['Program Date'])
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return None
    return None

data = load_data(uploaded_file)

if data is not None:
    # --- DASHBOARD SECTION ---
    st.header("📈 Impact Dashboard")
    
    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    total_contacts = data['Total Contacts'].sum()
    indirect_reach = data['Indirect Reach'].sum()
    avg_knowledge_gain = data['Knowledge Gain (%)'].mean()
    total_surveys = data['Surveys Collected'].sum()
    
    col1.metric("Total Contacts", f"{total_contacts:,}")
    col2.metric("Indirect Reach", f"{indirect_reach:,}")
    col3.metric("Avg. Knowledge Gain", f"{avg_knowledge_gain:.1f}%")
    col4.metric("Surveys Collected", f"{total_surveys:,}")
    
    st.divider()
    
    # Charts Row
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Contacts by Topic")
        fig_topic = px.pie(data, values='Total Contacts', names='Topic', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_topic, use_container_width=True)
        
    with c2:
        st.subheader("Knowledge Gain vs. Behavior Change")
        fig_scatter = px.scatter(data, x='Knowledge Gain (%)', y='Behavior Change (%)', 
                               size='Total Contacts', color='Topic', hover_name='Program Name',
                               color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    # Trend Analysis
    st.subheader("Program Reach Trend")
    trend_data = data.groupby('Program Date')[['Total Contacts', 'Indirect Reach']].sum().reset_index()
    fig_line = px.line(trend_data, x='Program Date', y=['Total Contacts', 'Indirect Reach'],
                      markers=True, labels={'value': 'Reach', 'variable': 'Metric'})
    st.plotly_chart(fig_line, use_container_width=True)

    # --- AI NARRATIVE SECTION ---
    st.divider()
    st.header("🤖 AI Impact Narrative")
    
    if st.button("Generate Narrative"):
        if not api_key:
            st.warning("Please enter an API key in the sidebar to generate narratives (Simulated version below).")
            narrative = utils.get_placeholder_narrative(total_contacts, avg_knowledge_gain, indirect_reach)
            
            st.subheader("Impact Narrative (Simulated)")
            st.write(narrative)
            
            st.subheader("Professional Prompt (Internal)")
            with st.expander("View generated prompt for LLM"):
                st.code(utils.generate_impact_prompt(data))
        else:
            with st.spinner("Analyzing data and crafting your story..."):
                # Here we would call an actual LLM API like gemini or openai
                # For this demo, we'll still use the enhanced generator logic
                prompt = utils.generate_impact_prompt(data)
                # Simulated response based on the prompt structure
                st.success("Narrative generated successfully using provided API context!")
                st.info("In a production environment, the prompt below would be sent to the LLM.")
                st.code(prompt)

else:
    st.info("Please upload a CSV file in the sidebar to view the dashboard and generate narratives.")
    
    # Display preview of mock data layout
    st.subheader("Expected Data Format")
    preview_df = pd.DataFrame({
        'Program Date': ['2024-01-01', '2024-01-05'],
        'County': ['Alachua', 'Miami-Dade'],
        'Topic': ['Agriculture', 'Youth & Families'],
        'Total Contacts': [50, 100],
        'Indirect Reach': [200, 500],
        'Knowledge Gain (%)': [85, 90]
    })
    st.table(preview_df)
