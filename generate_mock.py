import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Configuration
NUM_ROWS = 1000
START_DATE = datetime(2023, 1, 1)

# Options for generation
counties = ['Alachua', 'Miami-Dade', 'Hillsborough', 'Leon', 'Orange', 'Duval', 'Broward', 'Palm Beach', 'Pinellas', 'Lee']
topics = ['Agriculture', 'Youth & Families', 'Natural Resources', 'Community Development', 'Health & Nutrition']
program_types = ['Workshop', 'Field Day', 'Webinar', 'One-on-One Consultation', 'Interactive Demo']
audiences = ['Farmers', 'Homeowners', 'School Students', 'Local Businesses', 'General Public', 'Policy Makers']
feedbacks = [
    'Participants reported high satisfaction and immediate farm savings.',
    'Great hands-on learning experience for the kids.',
    'The webinar was highly informative but a bit too fast-paced.',
    'Learned how to maximize crop yields with less water.',
    'Will definitely apply these budgeting practices at home.',
    'Excellent resources provided for community development.',
    'Needed more time for Q&A, but the core material was excellent.',
    'The field demo completely changed how I think about soil health.',
    'Very engaging presentation, looking forward to the next one!',
    'The handouts were fantastic and easy to understand.'
]

# Generate Data
data = {
    'Program Date': [START_DATE + timedelta(days=random.randint(0, 365)) for _ in range(NUM_ROWS)],
    'County': [random.choice(counties) for _ in range(NUM_ROWS)],
    'Topic': [random.choice(topics) for _ in range(NUM_ROWS)],
    'Program Type': [random.choice(program_types) for _ in range(NUM_ROWS)],
    'Target Audience': [random.choice(audiences) for _ in range(NUM_ROWS)],
    'Total Contacts': np.random.randint(10, 500, size=NUM_ROWS),
    'Knowledge Gain (%)': np.random.randint(50, 100, size=NUM_ROWS),
    'Success Story': [random.choices(['Yes', 'No'], weights=[0.2, 0.8])[0] for _ in range(NUM_ROWS)]
}

# Derived or correlated columns
df = pd.DataFrame(data)
df['Program Name'] = df['Topic'] + " " + df['Program Type'] + " Series"
df['Indirect Reach'] = df['Total Contacts'] * np.random.randint(1, 10, size=NUM_ROWS)
df['Surveys Collected'] = (df['Total Contacts'] * np.random.uniform(0.3, 0.8, size=NUM_ROWS)).astype(int)
df['Behavior Change (%)'] = (df['Knowledge Gain (%)'] * np.random.uniform(0.5, 0.9, size=NUM_ROWS)).astype(int)

# Add qualitative feedback only to some rows to be realistic (mostly to Success Stories)
def get_feedback(row):
    if row['Success Story'] == 'Yes' or random.random() > 0.7:
        return random.choice(feedbacks)
    return np.nan

df['Qualitative Feedback'] = df.apply(get_feedback, axis=1)

# Ensure columns match exact schema order
final_cols = [
    'Program Date', 'County', 'Program Name', 'Topic', 'Total Contacts', 
    'Indirect Reach', 'Surveys Collected', 'Knowledge Gain (%)', 
    'Behavior Change (%)', 'Program Type', 'Target Audience', 
    'Success Story', 'Qualitative Feedback'
]
df = df[final_cols]
df = df.sort_values(by='Program Date')

# Save to CSV
df.to_csv('large_mock_data.csv', index=False)
print(f"✅ Successfully generated 'large_mock_data.csv' with {NUM_ROWS} records.")
