import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
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
    api_key_1 = st.text_input("Agent 1 API Key", type="password", help="Hardcoded to gpt-oss-20b for data analysis.")
    api_key_2 = st.text_input("Agent 2 API Key", type="password", help="Hardcoded to gpt-oss-120b for deliverables. Can be same as Agent 1.")
    
    st.divider()
    uploaded_file = st.file_uploader("Upload your data (CSV)", type="csv")
    
    st.info("Download the [mock_data.csv](https://github.com/siddy819/Extension-AI-Agent/blob/main/mock_data.csv) to test the dashboard.")

# --- DATA LOADING ---
@st.cache_data
def load_data(file):
    if file is not None:
        try:
            df = pd.read_csv(file)
            
            # Validate required columns
            required_cols = [
                'Program Date', 'County', 'Program Name', 'Topic', 'Total Contacts', 
                'Indirect Reach', 'Surveys Collected', 'Knowledge Gain (%)', 
                'Behavior Change (%)', 'Program Type', 'Target Audience', 
                'Success Story', 'Qualitative Feedback'
            ]
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"⚠️ **Data Format Error:** The uploaded CSV is missing the following required columns: `{', '.join(missing_cols)}`. Please match the Expected Data Format below.")
                return None
                
            df['Program Date'] = pd.to_datetime(df['Program Date'])
            return df
        except Exception as e:
            st.error(f"Error parsing CSV file: {e}")
            return None
    return None

data = load_data(uploaded_file)

if data is not None:
    st.sidebar.subheader("🎯 Dashboard Filters")
    all_counties = sorted(data['County'].unique())
    selected_counties = st.sidebar.multiselect("Select Counties", options=all_counties, default=all_counties)
    
    all_topics = sorted(data['Topic'].unique())
    selected_topics = st.sidebar.multiselect("Select Topics", options=all_topics, default=all_topics)
    
    # Reset AI state if filters change to prevent stale data in Agent memory
    current_selection = {'counties': selected_counties, 'topics': selected_topics}
    if 'last_filters' not in st.session_state:
        st.session_state.last_filters = current_selection
        
    if st.session_state.last_filters != current_selection:
        st.session_state.last_filters = current_selection
        st.session_state.narrative_output = None
        st.session_state.agent2_history = []
    
    # Apply filters
    data = data[(data['County'].isin(selected_counties)) & (data['Topic'].isin(selected_topics))]
    
    if data.empty:
        st.warning("No data available for the selected filters. Please adjust your selections.")
        st.stop()

    # --- DASHBOARD SECTION ---
    st.header("📈 Impact Dashboard")
    
    # KPI Row
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    total_events = len(data)
    total_contacts = data['Total Contacts'].sum()
    indirect_reach = data['Indirect Reach'].sum()
    avg_knowledge_gain = data['Knowledge Gain (%)'].mean()
    total_surveys = data['Surveys Collected'].sum()
    success_count = (data['Success Story'] == 'Yes').sum()
    
    col1.metric("Total Events", f"{total_events}")
    col2.metric("Total Contacts", f"{total_contacts:,}")
    col3.metric("Indirect Reach", f"{indirect_reach:,}")
    col4.metric("Avg. Knowledge", f"{avg_knowledge_gain:.1f}%")
    col5.metric("Surveys", f"{total_surveys:,}")
    col6.metric("Success Stories", f"{success_count}")
    
    st.divider()
    
    # Charts Row
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Contacts by Topic")
        fig_topic = px.pie(data, values='Total Contacts', names='Topic', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_topic, width='stretch')
        
    with c2:
        st.subheader("Knowledge Gain vs. Behavior Change")
        fig_scatter = px.scatter(data, x='Knowledge Gain (%)', y='Behavior Change (%)', 
                               size='Total Contacts', color='Topic', hover_name='Program Name',
                               hover_data=['Success Story', 'County', 'Target Audience'],
                               color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_scatter, width='stretch')
        
    # Trend Analysis
    st.subheader("Program Reach Trend")
    trend_data = data.groupby('Program Date')[['Total Contacts', 'Indirect Reach']].sum().reset_index()
    fig_line = px.line(trend_data, x='Program Date', y=['Total Contacts', 'Indirect Reach'],
                      markers=True, labels={'value': 'Reach', 'variable': 'Metric'},
                      color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_line, width='stretch')

    # New Qualitative Row
    st.divider()
    st.subheader("Qualitative Program Insights")
    q1, q2 = st.columns(2)
    
    with q1:
        st.subheader("Delivery Methods (Program Type)")
        fig_type = px.bar(data['Program Type'].value_counts().reset_index(), 
                         x='Program Type', y='count', color='Program Type',
                         labels={'Program Type': 'Type', 'count': 'Frequency'},
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_type, width='stretch')
        
    with q2:
        st.subheader("Success Story Distribution")
        fig_success = px.pie(data, names='Success Story', hole=0.4,
                           color_discrete_sequence=['#66c2a5', '#fc8d62']) # Green for Yes, Orange for No
        st.plotly_chart(fig_success, width='stretch')

    # --- MULTI-STEP AGENT CHAIN ---
    st.divider()
    st.header("🤖 Multi-Model Agent Chain")
    
    # Initialize session state for the narrative and Agent 2 history
    if 'narrative_output' not in st.session_state:
        st.session_state.narrative_output = None
    if 'agent2_history' not in st.session_state:
        st.session_state.agent2_history = [] # List of tuples (HumanMessage, AIMessage)

    # STEP 1: Agent 1 (Data -> Narrative)
    st.subheader("Step 1: Generate Core Narrative")
    if st.button("🚀 Run Agent 1"):
        if not api_key_1:
            st.warning("Please enter API Key 1 in the sidebar.")
        else:
            with st.spinner("Agent 1 (gpt-oss-20b) is analyzing data..."):
                prompt = utils.generate_impact_prompt(data)
                system_prompt = "You are a professional Florida Cooperative Extension reporting agent."
                # Stream the response
                response_container = st.empty()
                stream = utils.call_llm_stream(api_key_1, "gpt-oss-20b", system_prompt, prompt)
                full_response = response_container.write_stream(stream)
                
                if "Error" in full_response:
                    st.error(full_response)
                else:
                    st.session_state.narrative_output = full_response
                    st.success("Agent 1 Complete!")
                    response_container.empty() # Clear the stream container so it seamlessly shows below

    if st.session_state.narrative_output:
        st.info("Agent 1 Output:")
        st.markdown(st.session_state.narrative_output)
        
        st.divider()
        
        # STEP 2: Agent 2 (Narrative + User Input -> Specific Deliverable/Chat)
        st.subheader("Step 2: Interactive Deliverable & Chat")
        
        # Display Chat History for Agent 2
        for i, (human_msg, ai_msg) in enumerate(st.session_state.agent2_history):
            with st.chat_message("user"):
                st.write(human_msg.content)
            with st.chat_message("assistant"):
                st.write(ai_msg.content)

        st.divider()
        st.subheader("📥 Export Final Report")
        
        # Combine Agent 1 and Agent 2 results
        full_report = st.session_state.narrative_output
        if st.session_state.agent2_history:
            full_report += "\n\n---\n\n## AI Assistant Q&A\n\n"
            for h_msg, a_msg in st.session_state.agent2_history:
                full_report += f"**User:** {h_msg.content}\n\n"
                full_report += f"**Agent:** {a_msg.content}\n\n"
                
        pdf_bytes = utils.create_pdf(full_report)
        st.download_button(
            label="💾 Download Comprehensive Report (.pdf)",
            data=pdf_bytes,
            file_name="extension_impact_report.pdf",
            mime="application/pdf"
        )
        st.divider()

        # Prompt input for Agent 2
        user_instruction = st.chat_input("Ask Agent 2 to generate something or follow up...")
        
        if user_instruction:
            if not api_key_2:
                st.error("Please enter API Key 2 in the sidebar.")
            else:
                with st.spinner("Agent 2 (gpt-oss-120b) is responding..."):
                    # Construct Agent 2 context
                    # For the very first message, we include both the Agent 1 narrative AND the raw data
                    if not st.session_state.agent2_history:
                        raw_data_md = utils.format_data_for_agent(data)
                        enhanced_instruction = utils.generate_deliverable_prompt(
                            st.session_state.narrative_output, 
                            user_instruction, 
                            raw_data=raw_data_md
                        )
                    else:
                        enhanced_instruction = user_instruction
                    
                    system_prompt = utils.get_agent2_system_prompt()
                    
                    # Flatten history for LangChain [Human, AI, Human, AI...]
                    flat_history = []
                    for h, a in st.session_state.agent2_history:
                        flat_history.extend([h, a])
                    
                    # Actual API Call Stream
                    stream = utils.call_llm_stream(api_key_2, "gpt-oss-120b", system_prompt, enhanced_instruction, history=flat_history)
                    
                    with st.chat_message("assistant"):
                        full_response = st.write_stream(stream)
                    
                    if "Error" in full_response:
                        st.error(full_response)
                    else:
                        # Update history with rolling window of 10
                        new_human = HumanMessage(content=user_instruction)
                        new_ai = AIMessage(content=full_response)
                        st.session_state.agent2_history.append((new_human, new_ai))
                        
                        if len(st.session_state.agent2_history) > 10:
                            st.session_state.agent2_history.pop(0)
                        
                        st.rerun() # Refresh to show new messages in chat UI

else:
    st.info("Please upload a CSV file in the sidebar to view the dashboard and generate narratives.")
    
    # Display preview of mock data layout
    st.subheader("Expected Data Format")
    preview_df = pd.DataFrame({
        'Program Date': ['2024-01-15', '2024-02-05'],
        'County': ['Miami-Dade', 'Hillsborough'],
        'Program Name': ['Sustainable Urban Gardening', 'Healthy Snacking for Kids'],
        'Topic': ['Agriculture', 'Youth & Families'],
        'Total Contacts': [45, 120],
        'Indirect Reach': [120, 400],
        'Surveys Collected': [38, 90],
        'Knowledge Gain (%)': [85, 78],
        'Behavior Change (%)': [60, 45],
        'Program Type': ['Workshop', 'Interactive Demo'],
        'Target Audience': ['Homeowners', 'School Students'],
        'Success Story': ['Yes', 'No'],
        'Qualitative Feedback': ['Learned how to maximize yields.', 'High attendance but...']
    })
    st.table(preview_df)
