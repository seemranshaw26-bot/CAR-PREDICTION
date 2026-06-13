import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go

#PAGE CONFIGURATION
st.set_page_config(
    page_title="Car Prediction",
    page_icon="",
    layout="wide")

#CUSTOM CSS
st.markdown("""
    <style>
    .main {padding: 0rem 1rem;}
    h1 {color: #e74c3c; padding-bottom: 1rem;}
    </style>
    """, unsafe_allow_html=True)

#LOAD MODEL
@st.cache_resource
def load_model():
    try:
        model = joblib.load("Car_Prediction_Model.pkl")
        return model
    except FileNotFoundError:
        return None

#HEADER FILE
st.title("Car Price Prediction System")
st.markdown("### Get Instant Valuation For Your Used Car")

#LOAD MODEL
model = load_model()
if model is None:
    st.error("**Model Not Found**")
    st.info("""Please Run The Following Command First:
    ```
    python car_prediction_price.py
    ```
    this will help you predict your car price.
    """)
    st.stop()

#SIDEBAR INPUT
st.sidebar.title("Car Price Prediction System")
st.sidebar.subheader("Basic Information")
Year=st.sidebar.slider("Manufacturing Year", 2000, 2024,2015)
Present_Price=st.sidebar.number_input("Current Ex-Showroom Price(Lakhs)",0.0,50.0,5.0,0.1)
Kms_Driven=st.sidebar.number_input("Kms_Driven",0,500000,50000,1000)

st.sidebar.subheader("Car Specification")
Fuel_Type = st.sidebar.selectbox("Fuel_Type",['Petrol','Diesel','CNG'])
Seller_Type = st.sidebar.selectbox("Seller_Type",['Dealer','Individual'])
Transmission = st.sidebar.selectbox("Transmission",['Manual','Automatic'])
Owner = st.sidebar.selectbox("No.of Previous_Owner",[0,1,2,3])

#CALCULATION CAR AGE
Current_Year=2026
Car_Age= Current_Year-Year

#PREDICT BUTTON
st.sidebar.markdown("---")
Predict_Button=st.sidebar.button("Get Price Estimate",type="primary",use_container_width=True)

#MAIN CONTENT
import streamlit as fancy_st  # Assuming streamlit is imported as st

if Predict_Button:
    # 1. ENCODE CATEGORICAL VARIABLES
    fuel_encoded = {'Petrol': 2, 'Diesel': 1, 'CNG': 0}[Fuel_Type]
    seller_encoded = {'Dealer': 0, 'Individual': 1}[Seller_Type]
    transmission_encoded = {'Manual': 1, 'Automatic': 0}[Transmission]

    # 2. PREPARE INPUT DATAFRAME
    input_data = pd.DataFrame({
        'Year': [Year],
        'Present_Price': [Present_Price],
        'Kms_Driven': [Kms_Driven],
        'Fuel_Type': [fuel_encoded],
        'Seller_Type': [seller_encoded],
        'Transmission': [transmission_encoded],
        'Owner': [Owner]
    })

    # 3. MODEL PREDICTION
    # Ensure 'model' is loaded before this block (e.g., via pickle or joblib)
    Predicted_Price = model.predict(input_data)[0]

    # 4. CALCULATING DEPRECIATION
    Depreciation = Present_Price - Predicted_Price
    Depreciation_per = (Depreciation / Present_Price) * 100 if Present_Price > 0 else 0

    # 5. DISPLAY RESULTS
    st.markdown("---")
    st.header("Price Estimation Results")

    # MAIN METRICS
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Estimated Selling Price",
            f"₹{Predicted_Price:.2f} Lakhs",
            delta=None
        )
    with col2:
        st.metric(
            "Current Showroom Price",
            f"₹{Present_Price:.2f} Lakhs",
            delta=None
        )
    with col3:
        st.metric(
            "Total Depreciation",
            f"₹{Depreciation:.2f} Lakhs",
            delta=f"-{Depreciation_per:.1f}%"
        )

    # GAUGE CHART FOR PRICE RANGE
    st.markdown("---")
    st.subheader("Price Analysis")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Price range estimate (±10%)
        lower_estimate = Predicted_Price * 0.9
        upper_estimate = Predicted_Price * 1.1

        st.success(f"""
        **Expected Price Range:** ₹{lower_estimate:.2f}L - ₹{upper_estimate:.2f}L

        This is the typical market range for similar vehicles.
        """)

        # Price breakdown factors
        st.write("**Price Factors:**")
        factors = []

        if Car_Age <= 2:
            factors.append("Very new car - minimal depreciation")
        elif Car_Age <= 5:
            factors.append("Relatively new - good resale value")
        elif Car_Age <= 10:
            factors.append("Moderate age - average market value")
        else:
            factors.append("Older car - higher depreciation")

        if Kms_Driven < 30000:
            factors.append("Low mileage - adds value")
        elif Kms_Driven < 80000:
            factors.append("Average mileage")
        else:
            factors.append("High mileage - reduces value")

        if Transmission == 'Automatic':
            factors.append("Automatic transmission - premium pricing")

        if Fuel_Type == 'Diesel':
            factors.append("Diesel - preferred for high usage")
        elif Fuel_Type == 'Petrol':
            factors.append("Petrol - standard option")

        if Seller_Type == 'Dealer':
            factors.append("Dealer - may offer better warranty")

        for factor in factors:
            st.markdown(f"- {factor}")

    with col2:
        # Gauge chart setup
        max_price = Present_Price * 1.2

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=Predicted_Price,
            title={'text': "Estimated Price"},
            number={'prefix': "₹", 'suffix': "L"},
            gauge={
                'axis': {'range': [None, max_price]},
                'bar': {'color': "#e74c3c"},
                'steps': [
                    {'range': [0, Present_Price * 0.3], 'color': "lightgray"},
                    {'range': [Present_Price * 0.3, Present_Price * 0.7], 'color': "lightyellow"},
                    {'range': [Present_Price * 0.7, max_price], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "blue", 'width': 4},
                    'thickness': 0.75,
                    'value': Present_Price
                }
            }
        ))
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # Car details summary
    st.markdown("---")
    st.subheader("Your Car Details")

    details_col1, details_col2 = st.columns(2)

    with details_col1:
        st.write(f"**Manufacturing Year:** {Year}")
        st.write(f"**Car Age:** {Car_Age} years")
        st.write(f"**Kilometers Driven:** {Kms_Driven:,} km")
        st.write(f"**Fuel Type:** {Fuel_Type}")

    with details_col2:
        st.write(f"**Transmission:** {Transmission}")
        st.write(f"**Seller Type:** {Seller_Type}")
        st.write(f"**Previous Owners:** {Owner}")
        st.write(f"**Current Showroom Price:** ₹{Present_Price} Lakhs")

    # Tips for selling
    st.markdown("---")
    st.subheader("Tips to Get Better Price")
    st.markdown("""
    * **Keep it clean:** A well-detailed car fetches a better visual premium.
    * **Service Records:** Having a complete authorized service history builds trust.
    * **Fix minor dents:** Small fixes can disproportionately increase the perceived value.
    """)

else:
    # Initial page when button is not clicked
    st.markdown("---")
    st.info("Enter your car details in the sidebar and click **Get Price Estimate**")

    # Show example cars
    st.subheader("Example Valuations")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Recent Car**")
        st.write("Year: 2020")
        st.write("Price: ₹8.5L")
        st.write("Kms: 20,000")
        st.write("Est: ₹6.5-7.5L")

    with col2:
        st.write("**Mid-range Car**")
        st.write("Year: 2015")
        st.write("Price: ₹6.0L")
        st.write("Kms: 50,000")
        st.write("Est: ₹3.5-4.5L")

    with col3:
        st.write("**Older Car**")
        st.write("Year: 2010")
        st.write("Price: ₹5.0L")
        st.write("Kms: 100,000")
        st.write("Est: ₹1.5-2.5L")

    st.markdown("---")

    # Model info
    st.subheader("Model Information")
    col1, col2, col3 = st.columns(3)
    col1.metric("Algorithm", "ML Regression")
    col2.metric("Accuracy", "~85%")
    col3.metric("Dataset", "300+ cars")