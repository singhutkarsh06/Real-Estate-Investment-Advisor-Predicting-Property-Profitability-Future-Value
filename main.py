import pandas as pd
import datetime
from sklearn.preprocessing import LabelEncoder
import pickle

# ── LOAD ORIGINAL RAW FILE ────────────────────────────────
df = pd.read_csv(r"C:\Users\ACER\PycharmProjects\PythonProject1\india_housing_prices.csv")

print("✅ Raw file loaded. Shape:", df.shape)

current_year = datetime.datetime.now().year

# ── FIX 1: DROP DUPLICATE COLUMNS ────────────────────────
# Price_per_SqFt original has wrong values (0.10, 0.08 etc)
# Age_of_Property and Property_Age are same thing
df.drop(columns=['Price_per_SqFt', 'Age_of_Property'], inplace=True)
print("✅ Duplicate columns removed")

# ── NEW FEATURES ──────────────────────────────────────────
df['Price_per_SqFt_calc']  = (df['Price_in_Lakhs'] * 100000) / df['Size_in_SqFt']
df['School_Density_Score'] = df['Nearby_Schools'] / (df['Nearby_Hospitals'] + 1)
df['Transport_Score']      = df['Public_Transport_Accessibility'].map({'Low': 1, 'Medium': 2, 'High': 3}).fillna(1)
df['Infrastructure_Score'] = (df['Nearby_Schools'] + df['Nearby_Hospitals'] + df['Transport_Score']) / 3
df['Amenities_Count']      = df['Amenities'].apply(lambda x: len(str(x).split(',')))
df['Floor_Ratio']          = df['Floor_No'] / (df['Total_Floors'] + 1)
df['Property_Age']         = current_year - df['Year_Built']
df['Future_Price_5yr']     = df['Price_in_Lakhs'] * (1.08 ** 5)
print("✅ New features created")

# ── GOOD INVESTMENT LABEL ─────────────────────────────────
city_median = df.groupby('City')['Price_per_SqFt_calc'].transform('median')
df['Below_Median_Price'] = (df['Price_per_SqFt_calc'] <= city_median).astype(int)
df['Good_Investment'] = (
    ((df['BHK'] >= 3).astype(int) +
     (df['Infrastructure_Score'] >= 2).astype(int) +
     (df['Amenities_Count'] >= 3).astype(int) +
     df['Below_Median_Price']) >= 3
).astype(int)
print("✅ Good Investment label created")
print("   Distribution:", df['Good_Investment'].value_counts().to_dict())

# ── SAVE EDA FILE (with real city names) ─────────────────
df_eda = df.copy()
df_eda.to_csv(
    r"C:\Users\ACER\PycharmProjects\PythonProject1\india_housing_eda.csv",
    index=False
)
print("✅ EDA file saved with real city/state names")

# ── FIX 2: ENCODE Parking_Space & Security (missed before)
df['Parking_Space'] = df['Parking_Space'].map({'No': 0, 'Yes': 1})
df['Security']      = df['Security'].map({'No': 0, 'Yes': 1})
print("✅ Parking_Space and Security encoded")

# ── ENCODE ALL CATEGORICAL COLUMNS ───────────────────────
encode_cols = ['State', 'City', 'Locality', 'Property_Type',
               'Furnished_Status', 'Facing', 'Owner_Type',
               'Availability_Status', 'Public_Transport_Accessibility']

label_encoders = {}
for col in encode_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

print("✅ All categorical columns encoded")

# ── FIX 3: DROP Amenities TEXT column (not useful for ML)
df.drop(columns=['Amenities'], inplace=True)
print("✅ Raw Amenities text column removed (Amenities_Count kept)")

# ── SAVE ML FILE (with numbers for models) ────────────────
df.to_csv(
    r"C:\Users\ACER\PycharmProjects\PythonProject1\india_housing_processed.csv",
    index=False
)
print("✅ ML file saved with encoded values")

# ── SAVE ENCODERS for Streamlit ───────────────────────────
with open(r"C:\Users\ACER\PycharmProjects\PythonProject1\label_encoders.pkl", 'wb') as f:
    pickle.dump(label_encoders, f)
print("✅ Label encoders saved for Streamlit app")

# ── FINAL SUMMARY ─────────────────────────────────────────
print("\n========== SUMMARY ==========")
print("EDA file shape  :", df_eda.shape)
print("ML file shape   :", df.shape)
print("Columns in ML file:", df.columns.tolist())
print("Missing values  :", df.isnull().sum().sum())
print("==============================")



import pandas as pd

# Load and compress EDA file
df = pd.read_csv(r"C:\Users\ACER\PycharmProjects\PythonProject1\india_housing_eda.csv")
print("Original size:", df.shape)

# Keep only columns needed by the app
keep_cols = ['State', 'City', 'Locality', 'Property_Type', 'BHK',
             'Size_in_SqFt', 'Price_in_Lakhs', 'Floor_No', 'Total_Floors',
             'Year_Built', 'Nearby_Schools', 'Nearby_Hospitals',
             'Furnished_Status', 'Parking_Space', 'Security',
             'Public_Transport_Accessibility', 'Facing', 'Owner_Type',
             'Availability_Status', 'Price_per_SqFt_calc',
             'Infrastructure_Score', 'Amenities_Count', 'School_Density_Score',
             'Transport_Score', 'Floor_Ratio', 'Property_Age',
             'Future_Price_5yr', 'Good_Investment']

df = df[keep_cols]

# Save as compressed csv
df.to_csv(
    r"C:\Users\ACER\PycharmProjects\PythonProject1\india_housing_eda.csv",
    index=False
)
print("Compressed size:", df.shape)
print("Done!")