import streamlit as st
import pandas as pd
import openpyxl
import numpy as np
import requests
import json
import math
import seaborn as sns
import matplotlib.pyplot as plt

#needful functions
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def scaling(x):
  if x == "Strongly Disagree":
    x = 1
  elif x == "Disagree":
    x = 2
  elif x == "Neutral":
    x = 3
  elif x == "Agree":
    x = 4
  elif x == "Strongly Agree":
    x = 5
  return x

#progress bar
def spinner(value):
    return math.ceil(100/value)

#getting the mean of the likert scale columns
def mean_score(row):
    global main_cols
    main_cols = list(data.columns[14:])
    a1 = np.array([row[main_cols[i]] for i in range(0,6)])
    row["Job Satisfaction"] = a1.mean()
    a2 = np.array([row[main_cols[i]] for i in range(6,11)])
    row["Alternative Job Opportunity"] = a2.mean()
    a3 = np.array([row[main_cols[i]] for i in range(11,17)])
    row["Recognition"] = a3.mean()
    a4 = np.array([row[main_cols[i]] for i in range(17,22)])
    row["Organizational Support"] = a4.mean()
    a5 = np.array([row[main_cols[i]] for i in range(22,28)])
    row["Job Stress"] = a5.mean()
    a6 = np.array([row[main_cols[i]] for i in range(28,32)])
    row["Organizational Commitment"] = a6.mean()

    return row

#call the fpredictions through endpoint
def get_prediction(data):
  url = 'https://askai.aiclub.world/49e280b7-4939-4bc3-b8d0-7058138a6198'
  r = requests.post(url, data=json.dumps(data))
  response = getattr(r,'_content').decode("utf-8")
  print(response)
  return response

#web app
#title
st.title("Turnover Intentions Analysis of Frontend and Banckend Developers")

#setting the image
st.image("developers.jpg", caption = "Frontend & Backend Developers")

#expander to about say about the project
with st.expander("About the Project 📑"):
    st.subheader("The Project")
    st.markdown("- This project is mainly focused on predicting the turnover intentions of frontned and backend developers")
    st.markdown("- Data is collected from 203 respondents.")
    st.markdown("- Model is build on demograhic variables and on some likert scale variables.")

#tabs to naviage
tab1, tab2 = st.tabs(["Introduction 📊","Predictions 💻"])

with tab1:
    st.subheader("Dataset")
    #reading the dataset
    data1 = pd.read_csv("Research_final_data.csv")
    st.dataframe(data1)

    #feature impotance
    st.subheader("Main Variables which impact the Turnover Intentions")
    st.image("features.png", caption = "Feature Importance")

    #correlation analysis
    st.subheader("Correlation analysis")
    st.image("correlations.png")

with tab2:
    st.header("Prediction Dashboard")
    st.markdown("- User can upload a csv sheet to the web.")
    st.markdown("- The predictions can be viewed or downloaded as user preference")

    #prediction dashboard
    #get the link
    st.subheader("Predict the Turnover Intention")
    file = st.file_uploader("Please upload a file")

    if file:
        name_file = file.name
        if not (name_file.endswith(".csv") or name_file.endswith(".xlsx")):
            st.error("Unsupported File extension. Please upload a csv or xlsx", icon="🚨")
        else:
            #show the uploaded csv file
            if name_file.endswith(".csv"):
                data = pd.read_csv(file)
                download_data = data.copy()
                st.subheader("User Data")
                st.dataframe(data)

            if name_file.endswith(".xlsx"):
                data = pd.read_excel(file, engine = 'openpyxl')
                download_data = data.copy()
                st.subheader("User Data")
                st.dataframe(data)

            if st.button("Start Predictions"):
                my_bar = st.progress(0)
                #dropping the first column
                data.drop(list(data.columns)[0], axis = 1, inplace = True)
                #scaling the likert scale values
                data = data.applymap(scaling)
                #getting the mean likert scale values
                data = data.apply(mean_score, axis = 1)
                #dropping the likertscales
                data.drop(main_cols, axis = 1, inplace = True)

                #converting the dataframe rows to dictionary
                data_dict = data.to_dict("records")
                final_predictions = []

                #progress bar
                multi = spinner(len(data))

                #getting the predictions
                for index,input in enumerate(data_dict):
                    response = get_prediction(input)
                    response = json.loads(response)
                    response = json.loads(response['body'])
                    score = response['score']
                    prediction = response['predicted_label']
                    final_predictions.append(prediction)
                    p_value = (index + 1)*multi
                    if p_value > 100:
                        p_value = 100
                    my_bar.progress(p_value)

                #setting the final dataframe to download
                download_data["Turnover Intention"] = final_predictions

                #predictions
                st.subheader("Predictions")
                lab_data = download_data["Turnover Intention"].value_counts()
                fig = plt.figure(figsize=(5,5))
                plt.bar(lab_data.index, [int(i) for i in lab_data.values])
                plt.xlabel("Turnover Intention")
                plt.ylabel("Frequency")
                plt.title("Predictions on Turnover Intentions")
                st.pyplot(fig)

                #download the file
                csv = convert_df(download_data)
                btn = st.download_button("PLease the Download the Results", csv, file_name = "prediction.csv", mime='text/csv', disabled=False)

                
                        
                    
                    

    

