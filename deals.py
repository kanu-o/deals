# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 14:02:09 2025

@author: Kanu George
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pd.options.future.infer_string = True

st.title("Sales Performance Through Probabilistic Analysis")
st.write("Select a name to get started")

# List of names
names = ["Select a name", "Amir", "Karl", "Splendor", "Shalom", "Tosin", "John", "Tessa", "Sekinat"]

#Dropdown
selected_name = st.selectbox("Choose a name", names)

# Only run the rest of the code below if valid name is chosen
if selected_name != "Select a name":
    st.write(f"You selected: {selected_name}")
    uploaded_file = st.file_uploader("Choose a file")
    
    #--------------- PHASE 2 ----------------
    # DATA INGESTION AND CLEANING
    
    if uploaded_file is not None:
    
        try:
            file_name = uploaded_file.name.lower()
    
            # Detect file type by extension
            if file_name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif file_name.endswith(".xls") or file_name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            else:
                st.error("Unsupported file type: Please upload a CSV or Excel file.")
                st.stop()
    
            # Remove duplicate rows
            df.drop_duplicates(inplace=True)
    
            # Rename column if it exists
            if "Unnamed: 0" in df.columns:
                df.rename(columns={"Unnamed: 0": "sales_pitch_id"}, inplace=True)
    
            # Validation check
            req_columns = {"status", "client", "product", "amount"}
            missing_cols = req_columns - set(df.columns)
    
            if missing_cols:
                st.error(f"The uploaded file is missing required columns: {missing_cols}")
                st.stop()
    
            # Convert amount to absolute value
            df['amount'] = df['amount'].abs()
    
            st.success(f"{uploaded_file.name} has been cleaned and validated.")
    
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")
            st.stop()
    
    
        
        #------------- PHASE 3: CORE METRICS ---------------------
        
        # Success and loss probabilities
        p_success = (df['status'] == "Won").mean().round(4) * 100
        p_loss = (df['status'] == "Lost").mean().round(4) * 100
        
        # Win-rate per client type
        new_client_win = (df[df["client"] == "New"]["status"] == "Won").mean().round(3) * 100
        current_client_win = (df[df["client"] == "Current"]["status"] == "Won").mean().round(3) * 100
        
        # Spread (standard deviation of the amount)
        amount_std = round(df['amount'].std(), 3)
        
        # Status storage (won = 1, lost = 0)
        status_bin = (df['status'] == "Won").astype(int).tolist()
        
        # Function to compute longest streak
        def longest_streak(collection, value): 
            max_run = 0
            current = 0
            for c in collection:
                if c == value:
                    current += 1
                    max_run = max(max_run, current)
                else:
                    current = 0
            return max_run
        
        longest_win_streak = longest_streak(status_bin, 1)
        longest_loss_streak = longest_streak(status_bin, 0)
        
        # Conditional probabilities
        after_win = []
        after_loss = []
        
        for i in range(len(status_bin) - 1):  # stop at second-to-last index
            if status_bin[i] == 1:
                after_win.append(status_bin[i + 1])
            else:
                after_loss.append(status_bin[i + 1])
        
        p_win_after_win = np.mean(after_win).round(4) * 100 if after_win else 0
        p_win_after_loss = np.mean(after_loss).round(4) * 100 if after_loss else 0
        
        st.write("")
        st.write("")
        
        #--------------- PHASE 4: SUMMARY TABLE ------------------
        st.subheader(f"{selected_name}'s Performance:")
        
        data = {
            "Metrics": [
                "Success Rate",
                "Failure Rate",
                "New Client Win Rate",
                "Current Client Win Rate",
                "Longest Win Streak",
                "Longest Loss Streak",
                "Probability of a win after a win",
                "Probability of a win after a loss",
                "Spread"
            ],
            "Values": [
                p_success,
                p_loss,
                new_client_win,
                current_client_win,
                longest_win_streak,
                longest_loss_streak,
                p_win_after_win,
                p_win_after_loss,
                amount_std
            ]
        }
        
        data_df = pd.DataFrame(data)
        st.dataframe(data_df, use_container_width=True)
        
        st.write("")
        st.write("")
         #--------------- PHASE 5: VISUALIZATION ------------------
        st.subheader("Performance Visuals")
        
        fig, ax = plt.subplots()
        ax.hist(df['amount'], color='firebrick', edgecolor="white")
        ax.set_title(f"Distribution of {selected_name}'s Sales Amount", color="white")
      
        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")
        
        # Transparent background
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        st.pyplot(fig)
        
        st.write("")
        
        # --------- TOP 5 PRODUCT BY WINRATE ----------
        product_winrate = (
            df.groupby("product")["status"]
              .apply(lambda x: (x == "Won").mean() * 100)
              .round(2)
        )
        
        top_5_product_winrate = product_winrate.sort_values(ascending=False).head(5)

        fig,ax = plt.subplots()
        bars = ax.bar(top_5_product_winrate.index, top_5_product_winrate.values,
                      color='blue', edgecolor="white")
        ax.bar_label(
            bars,
            labels=[f"{v:.1f}%" for v in top_5_product_winrate.values],
            color="white")

        ax.set_title("Top 5 Product's by Win Rate%.", color="white")
        ax.set_xticklabels(top_5_product_winrate.index, rotation=45, ha="right")

        
        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")
        
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        st.pyplot(fig)
else:
    st.warning("Please select a valid name to continue.")
        

