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
                # Actual API Call
                response = utils.call_llm(api_key_1, "gpt-oss-20b", system_prompt, prompt)
                
                if "Error" in response:
                    st.error(response)
                else:
                    st.session_state.narrative_output = response
                    st.success("Agent 1 Complete!")

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

        # Prompt input for Agent 2
        user_instruction = st.chat_input("Ask Agent 2 to generate something or follow up...")
        
        if user_instruction:
            if not api_key_2:
                st.error("Please enter API Key 2 in the sidebar.")
            else:
                with st.spinner("Agent 2 (gpt-oss-120b) is responding..."):
                    # Construct Agent 2 context
                    # For the very first message, we include the Agent 1 narrative as prefix context
                    if not st.session_state.agent2_history:
                        enhanced_instruction = f"Based on this impact narrative: '{st.session_state.narrative_output}', please execute this instruction: {user_instruction}"
                    else:
                        enhanced_instruction = user_instruction
                    
                    system_prompt = "You are an AI Communications Specialist for Florida Cooperative Extension. Use Agent 1's narrative as your core data source."
                    
                    # Flatten history for LangChain [Human, AI, Human, AI...]
                    flat_history = []
                    for h, a in st.session_state.agent2_history:
                        flat_history.extend([h, a])
                    
                    # Actual API Call
                    response_text = utils.call_llm(api_key_2, "gpt-oss-120b", system_prompt, enhanced_instruction, history=flat_history)
                    
                    if "Error" in response_text:
                        st.error(response_text)
                    else:
                        # Update history with rolling window of 10
                        new_human = HumanMessage(content=user_instruction)
                        new_ai = AIMessage(content=response_text)
                        st.session_state.agent2_history.append((new_human, new_ai))
                        
                        if len(st.session_state.agent2_history) > 10:
                            st.session_state.agent2_history.pop(0)
                        
                        st.rerun() # Refresh to show new messages in chat UI

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
