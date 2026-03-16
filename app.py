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
    st.header("🔑 Agent Credentials")
    api_key_1 = st.text_input("Agent 1 API Key (Narrative)", type="password", help="Used to analyze data and write the core narrative.")
    api_key_2 = st.text_input("Agent 2 API Key (Deliverables)", type="password", help="Used to transform the narrative into custom outputs. Can be same as Agent 1.")
    
    st.divider()
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

    # --- MULTI-STEP AGENT CHAIN ---
    st.divider()
    st.header("🤖 Multi-Model Agent Chain")
    
    # Initialize session state for the narrative
    if 'narrative_output' not in st.session_state:
        st.session_state.narrative_output = None

    # STEP 1: Agent 1 (Data -> Narrative)
    st.subheader("Step 1: Generate Core Narrative")
    if st.button("🚀 Run Agent 1"):
        if not api_key_1:
            st.warning("Please enter API Key 1 in the sidebar (Simulated narrative below).")
            st.session_state.narrative_output = utils.get_placeholder_narrative(total_contacts, avg_knowledge_gain, indirect_reach)
        else:
            with st.spinner("Agent 1 is analyzing data..."):
                # Simulation of Agent 1 logic
                st.session_state.narrative_output = utils.get_placeholder_narrative(total_contacts, avg_knowledge_gain, indirect_reach)
                st.success("Agent 1 Complete!")

    if st.session_state.narrative_output:
        st.info("Agent 1 Output:")
        st.markdown(st.session_state.narrative_output)
        
        st.divider()
        
        # STEP 2: Agent 2 (Narrative + User Input -> Specific Deliverable)
        st.subheader("Step 2: Interactive Deliverable Generation")
        user_instruction = st.text_area("What should Agent 2 generate from this narrative?", 
                                      placeholder="e.g., 'Write a 3-post LinkedIn thread highlighting the behavior change.' or 'Draft a thank-you email for donors focus on the Community Impact.'")
        
        if st.button("✨ Run Agent 2"):
            if not user_instruction:
                st.error("Please provide instructions for Agent 2.")
            elif not api_key_2 and api_key_1: # If they gave key 1 but not key 2, assume they might want to use key 1
                st.warning("No Key 2 provided. Using Key 1 for Agent 2 (Simulated).")
            
            with st.spinner("Agent 2 is crafting your deliverable..."):
                # Generate Agent 2 Prompt
                agent2_prompt = utils.generate_deliverable_prompt(st.session_state.narrative_output, user_instruction)
                
                st.success("Agent 2 Complete!")
                st.subheader("Final Deliverable")
                # Placeholder for Deliverable
                st.info(f"Generated based on instruction: '{user_instruction}'")
                st.markdown(f"**[SIMULATED OUTPUT]**\n\nThis is where the output from the second LLM would appear. It would have processed the Agent 1 narrative using your specific instructions:\n\n*\"{user_instruction}\"*")
                
                with st.expander("View Agent 2 Prompt Context"):
                    st.code(agent2_prompt)

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
