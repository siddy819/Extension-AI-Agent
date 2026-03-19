import os
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

def call_llm(api_key, model_name, system_prompt, human_prompt, history=None):
    """
    Performs a real API call to the UF IT enterprise endpoint using LangChain.
    Supports a rolling history of messages.
    """
    try:
        chat = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base="https://api.ai.it.ufl.edu",
            model=model_name,
            temperature=0.1
        )
        
        messages = [SystemMessage(content=system_prompt)]
        
        # Add history if provided (expected as list of SystemMessage/HumanMessage/AIMessage)
        if history:
            messages.extend(history)
            
        # Add the current human prompt
        messages.append(HumanMessage(content=human_prompt))
        
        response = chat.invoke(messages)
        return response.content
    except Exception as e:
        return f"Error calling LLM: {str(e)}"

def call_llm_stream(api_key, model_name, system_prompt, human_prompt, history=None):
    """
    Performs a real API call to the UF IT enterprise endpoint using LangChain.
    Yields chunks for streaming output in Streamlit.
    """
    try:
        chat = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base="https://api.ai.it.ufl.edu",
            model=model_name,
            temperature=0.1,
            streaming=True
        )
        
        messages = [SystemMessage(content=system_prompt)]
        
        if history:
            messages.extend(history)
            
        messages.append(HumanMessage(content=human_prompt))
        
        for chunk in chat.stream(messages):
            yield chunk.content
    except Exception as e:
        yield f"\n\n🚨 Error calling LLM: {str(e)}"

def generate_impact_prompt(data):
    """
    Creates a detailed prompt for the LLM based on summarized Extension metrics.
    Includes qualitative insights from the expanded mock data.
    """
    total_contacts = data['Total Contacts'].sum()
    indirect_reach = data['Indirect Reach'].sum()
    avg_knowledge = data['Knowledge Gain (%)'].mean()
    top_topic = data['Topic'].mode()[0]
    
    # New metrics for Agent 1
    success_rate = (data['Success Story'] == 'Yes').mean() * 100
    top_audience = data['Target Audience'].mode()[0]
    
    summary_stats = data.groupby('Topic')[['Total Contacts', 'Surveys Collected', 'Knowledge Gain (%)']].mean().to_string()
    
    # Get a few distinctive qualitative feedback snippets
    feedback_samples = data[data['Qualitative Feedback'].notna()]['Qualitative Feedback'].head(5).tolist()
    feedback_text = "\n- ".join(feedback_samples)

    prompt = f"""
    You are an AI Agent specialized in Florida Cooperative Extension reporting. 
    Your goal is to transform the following raw metrics and qualitative insights into a professional 'Impact Narrative'.

    GLOBAL METRICS:
    - Total Direct Contacts: {total_contacts:,}
    - Total Indirect Reach: {indirect_reach:,}
    - Average Knowledge Gain: {avg_knowledge:.1f}%
    - Overall Success Story Rate: {success_rate:.1f}%
    - Most Frequent Focus Area: {top_topic}
    - Primary Target Audience: {top_audience}

    TOPIC-LEVEL BREAKDOWN:
    {summary_stats}

    SELECTED QUALITATIVE FEEDBACK:
    - {feedback_text}

    TASKS:
    1. Write a 3-paragraph professional 'Impact Narrative' following UF/IFAS standards. 
       - Paragraph 1: Quantitative reach and focus.
       - Paragraph 2: Knowledge gain and specific success story highlights.
       - Paragraph 3: Long-term community impact and qualitative sentiment.
    2. Provide a 3-bullet point 'Executive Summary' for leadership.
    3. Suggest one 'Champion Quote' based on the qualitative feedback provided.

    TONE: Professional, authoritative yet community-focused, and results-oriented.
    """
    return prompt

def generate_deliverable_prompt(narrative, user_instruction, raw_data=None):
    """
    Creates a prompt for the second agent based on Agent 1's narrative, 
    user input, and optional raw data context.
    """
    data_context = ""
    if raw_data is not None:
        data_context = f"\nRAW DATA CONTEXT:\n---\n{raw_data}\n---\n"

    prompt = f"""
    You are an AI Communications Specialist for Florida Cooperative Extension.
    
    INPUT NARRATIVE FROM AGENT 1:
    ---
    {narrative}
    ---
    {data_context}
    
    USER INSTRUCTION:
    {user_instruction}
    
    TASK:
    Based on the input narrative and the raw data context, execute the user instruction exactly. 
    Ensure the output maintains the professional and impactful tone of the Extension service.
    """
    return prompt

def format_data_for_agent(df):
    """
    Converts the dataframe to a concise markdown table for LLM context.
    """
    # Keep essential columns to save tokens while providing full context
    cols = ['Program Date', 'County', 'Program Name', 'Topic', 'Total Contacts', 'Indirect Reach',
            'Knowledge Gain (%)', 'Behavior Change (%)', 'Program Type', 'Target Audience', 
            'Success Story', 'Qualitative Feedback']
    return df[cols].to_markdown(index=False)

def get_placeholder_narrative(total_contacts, avg_knowledge_gain, indirect_reach):
    """Fallback narrative if no API key is provided."""
    return f"""
Program Overview: In 2024, the Florida Cooperative Extension program successfully reached a total of {total_contacts:,} direct participants across various focus areas, including Agriculture and Natural Resources.

Key Outcomes: Evaluation data indicates a significant success in knowledge transfer, with an average {avg_knowledge_gain:.1f}% knowledge gain reported by participants. Notably, behavior change was observed in approximately {avg_knowledge_gain-20:.1f}% of survey respondents, demonstrating the practical application of Extension research.

Community Impact: Beyond direct education, the indirect reach of {indirect_reach:,} underscores the cascading effect of Extension programs in strengthening Florida's local communities and ecosystems.
    """
