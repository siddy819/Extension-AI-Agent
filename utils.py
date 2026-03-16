import os
import pandas as pd
# Hypothetical library imports - we'll use a generic approach
# for the prompt engineering to make it adaptable.

def generate_impact_prompt(data):
    """
    Creates a detailed prompt for the LLM based on summarized Extension metrics.
    """
    total_contacts = data['Total Contacts'].sum()
    indirect_reach = data['Indirect Reach'].sum()
    avg_knowledge = data['Knowledge Gain (%)'].mean()
    top_topic = data['Topic'].mode()[0]
    
    summary_stats = data.groupby('Topic')[['Total Contacts', 'Surveys Collected', 'Knowledge Gain (%)']].mean().to_string()

    prompt = f"""
    You are an AI Agent specialized in Florida Cooperative Extension reporting. 
    Your goal is to transform the following raw metrics into a professional 'Impact Narrative'.

    GLOBAL METRICS:
    - Total Direct Contacts: {total_contacts:,}
    - Total Indirect Reach: {indirect_reach:,}
    - Average Knowledge Gain: {avg_knowledge:.1f}%
    - Most Frequent Topic: {top_topic}

    TOPIC-LEVEL BREAKDOWN:
    {summary_stats}

    TASKS:
    1. Write a 3-paragraph professional 'Impact Narrative' following UF/IFAS standards. Focus on the value provided to the community.
    2. Provide a 3-bullet point 'Executive Summary' for leadership.
    3. Suggest one 'Success Story' headline based on these numbers.

    TONE: Professional, academic yet accessible, and results-oriented.
    """
    return prompt

def generate_deliverable_prompt(narrative, user_instruction):
    """
    Creates a prompt for the second agent based on Agent 1's narrative and user input.
    """
    prompt = f"""
    You are an AI Communications Specialist for Florida Cooperative Extension.
    
    INPUT NARRATIVE FROM AGENT 1:
    ---
    {narrative}
    ---
    
    USER INSTRUCTION:
    {user_instruction}
    
    TASK:
    Based on the input narrative, execute the user instruction exactly. 
    Ensure the output maintains the professional and impactful tone of the Extension service.
    """
    return prompt

def get_placeholder_narrative(total_contacts, avg_knowledge_gain, indirect_reach):
    """Fallback narrative if no API key is provided."""
    return f"""
Program Overview: In 2024, the Florida Cooperative Extension program successfully reached a total of {total_contacts:,} direct participants across various focus areas, including Agriculture and Natural Resources.

Key Outcomes: Evaluation data indicates a significant success in knowledge transfer, with an average {avg_knowledge_gain:.1f}% knowledge gain reported by participants. Notably, behavior change was observed in approximately {avg_knowledge_gain-20:.1f}% of survey respondents, demonstrating the practical application of Extension research.

Community Impact: Beyond direct education, the indirect reach of {indirect_reach:,} underscores the cascading effect of Extension programs in strengthening Florida's local communities and ecosystems.
    """
