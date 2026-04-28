import pandas as pd
import random
import numpy as np

def generate_fake_data(num_samples=100):
    """
    Generates 100 samples of churn data with some "dirty" features for preprocessing.
    """
    data = []
    
    genders = ['Male', 'Female', 'male', 'FEMALE', 'Other']
    subs_types = ['Basic', 'Standard', 'Premium', 'basic', 'PREMIUM']
    contract_lengths = ['Monthly', 'Quarterly', 'Annual', 'monthly', 'ANNUAL']
    
    for _ in range(num_samples):
        # Customer ID: random CSTxx
        customer_id = f"CST{random.randint(1, 999):02d}"
        
        # Age: 18-80, but let's add some outliers
        age = random.randint(18, 80)
        if random.random() < 0.05:
            age = random.choice([150, -5, 0]) # Dirty data
            
        gender = random.choice(genders)
        
        tenure = random.randint(1, 60) # months
        usage_freq = random.randint(1, 30) # times/month
        support_calls = random.randint(0, 10)
        payment_delay = random.randint(0, 30) # days
        
        subs_type = random.choice(subs_types)
        contract_length = random.choice(contract_lengths)
        
        total_spend = round(random.uniform(100, 5000), 2)
        if random.random() < 0.05:
            total_spend = -random.randint(10, 100) # Negative spend
            
        last_interaction = random.randint(1, 30) # days ago
        
        row = {
            "CustomerID": customer_id,
            "Age": age,
            "Gender": gender,
            "Tenure": tenure,
            "Usage Frequency": usage_freq,
            "Support Calls": support_calls,
            "Payment Delay": payment_delay,
            "Subscription Type": subs_type,
            "Contract Length": contract_length,
            "Total Spend": total_spend,
            "Last Interaction": last_interaction
        }
        
        # Introduce missing values (dirty data)
        for key in row.keys():
            if key != "CustomerID" and random.random() < 0.03: # 3% chance of missing value
                row[key] = np.nan
                
        data.append(row)
        
    return data
