# Import the necessary libraries
import re
import csv
import pandas as pd

# Load the concepts.csv
df = pd.read_csv('concepts.csv')

# For each row in the DataFrame, print the "Name" and update the "Cleaned Name" column
for _, row in df.iterrows():
    print(f"Original Name: {row['Name']}")
    # For each Name, remove the numeroration like 1.5 in the given example with a regex pattern
    name = row['Name']
    # Use re.sub to remove the matched prefix
    name = re.sub(r'^\d+(\.\d+)*\s*', '', name)
    # Trim leading and trailing white spaces from the Name
    name = name.strip()

    # Print the updated Name
    print(f"Updated Name: {name}")
    # Update the "Name" column in the DataFrame with the updated Name
    df.at[_, 'Name'] = name

# Save the updated DataFrame to a new CSV file named 'cleaned_concepts.csv'
df.to_csv('cleaned_concepts.csv', index=False, quoting=csv.QUOTE_NONNUMERIC)
print("Concepts cleaned and saved successfully!")