import pandas as pd
import pickle
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor


# Load dataset
df = pd.read_csv("car data.csv")

print("Columns found:")
print(df.columns.tolist())


# ---------------------------------------------------------
# Rename columns to standard names
# ---------------------------------------------------------

df = df.rename(columns={
    "Year": "Year",
    "Present_Price": "Present_Price",
    "Kms_Driven": "Kms_Driven",
    "Fuel_Type": "Fuel_Type",
    "Seller_Type": "Seller_Type",
    "Transmission": "Transmission",
    "Owner": "Owner",
    "Selling_Price": "Selling_Price"
})


# ---------------------------------------------------------
# Convert categorical columns
# ---------------------------------------------------------

df["Fuel_Type"] = df["Fuel_Type"].map({
    "Petrol": 0,
    "Diesel": 1,
    "CNG": 2
})


df["Seller_Type"] = df["Seller_Type"].map({
    "Dealer": 0,
    "Individual": 1
})


df["Transmission"] = df["Transmission"].map({
    "Manual": 0,
    "Automatic": 1
})


# ---------------------------------------------------------
# Remove invalid rows
# ---------------------------------------------------------

df = df.dropna()


# ---------------------------------------------------------
# Features
# ---------------------------------------------------------

X = df[
    [
        "Year",
        "Present_Price",
        "Kms_Driven",
        "Fuel_Type",
        "Seller_Type",
        "Transmission",
        "Owner"
    ]
]


y = df["Selling_Price"]


# ---------------------------------------------------------
# Train/test split
# ---------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


# ---------------------------------------------------------
# Train model
# ---------------------------------------------------------

model = RandomForestRegressor(
    n_estimators=300,
    random_state=42
)


model.fit(X_train, y_train)


# ---------------------------------------------------------
# Save model
# ---------------------------------------------------------

os.makedirs("model", exist_ok=True)


with open(
    "model/car_price_model.pkl",
    "wb"
) as file:

    pickle.dump(model, file)


print()
print("======================================")
print("MODEL TRAINED SUCCESSFULLY")
print("======================================")
print()
print("Saved to:")
print("model/car_price_model.pkl") 
import pandas as pd
import pickle
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor


# Load dataset
df = pd.read_csv("car data.csv")

print("Columns found:")
print(df.columns.tolist())


# ---------------------------------------------------------
# Rename columns to standard names
# ---------------------------------------------------------

df = df.rename(columns={
    "Year": "Year",
    "Present_Price": "Present_Price",
    "Kms_Driven": "Kms_Driven",
    "Fuel_Type": "Fuel_Type",
    "Seller_Type": "Seller_Type",
    "Transmission": "Transmission",
    "Owner": "Owner",
    "Selling_Price": "Selling_Price"
})


# ---------------------------------------------------------
# Convert categorical columns
# ---------------------------------------------------------

df["Fuel_Type"] = df["Fuel_Type"].map({
    "Petrol": 0,
    "Diesel": 1,
    "CNG": 2
})


df["Seller_Type"] = df["Seller_Type"].map({
    "Dealer": 0,
    "Individual": 1
})


df["Transmission"] = df["Transmission"].map({
    "Manual": 0,
    "Automatic": 1
})


# ---------------------------------------------------------
# Remove invalid rows
# ---------------------------------------------------------

df = df.dropna()


# ---------------------------------------------------------
# Features
# ---------------------------------------------------------

X = df[
    [
        "Year",
        "Present_Price",
        "Kms_Driven",
        "Fuel_Type",
        "Seller_Type",
        "Transmission",
        "Owner"
    ]
]


y = df["Selling_Price"]


# ---------------------------------------------------------
# Train/test split
# ---------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


# ---------------------------------------------------------
# Train model
# ---------------------------------------------------------

model = RandomForestRegressor(
    n_estimators=300,
    random_state=42
)


model.fit(X_train, y_train)


# ---------------------------------------------------------
# Save model
# ---------------------------------------------------------

os.makedirs("model", exist_ok=True)


with open(
    "model/car_price_model.pkl",
    "wb"
) as file:

    pickle.dump(model, file)


print()
print("======================================")
print("MODEL TRAINED SUCCESSFULLY")
print("======================================")
print()
print("Saved to:")
print("model/car_price_model.pkl")