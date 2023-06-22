# -*- coding: utf-8 -*-
"""
Created on  30 -4-2023 

@author: sara
"""

import streamlit as st

st.write("""
# Her2Inhibitors
""")
import pandas as pd
from PIL import Image
import subprocess
import os
import base64
import pickle
from padelpy import padeldescriptor
import glob
# Molecular descriptor calculator
def desc_calc():
    # Performs the descriptor calculation
    bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    os.remove('molecule.smi')
def desc_calc1():
   
    fingerprint = 'PubchemFingerprinter'

    fingerprint_output_file = ''.join([fingerprint,'.csv']) #Substructure.csv
    fingerprint_descriptortypes = 'PubchemFingerprinter.xml'
    
    padeldescriptor(mol_dir='molecule.smi', 
                    d_file='descriptors_output.csv', #'Substructure.csv'
                    #descriptortypes='SubstructureFingerprint.xml', 
                    descriptortypes= fingerprint_descriptortypes,
                    detectaromaticity=True,
                    standardizenitro=True,
                    standardizetautomers=True,
                    threads=2,
                    removesalt=True,
                    log=True,
                    fingerprints=True)

# File download
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
    return href

# Model building
def build_model(input_data):
    # Reads in saved regression model
    load_model = pickle.load(open('Her2_model.pkl', 'rb'))
    # Apply model to make predictions
    prediction = load_model.predict(input_data)
    st.header('**Prediction output**')
    prediction_output = pd.Series(prediction, name='bioactivity_class')
    molecule_name = pd.Series(load_data[0], name='molecule_smile')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.write(df)
    st.markdown(filedownload(df), unsafe_allow_html=True)

# # Logo image
# image = Image.open('her2breastcancer.png')

# st.image(image, use_column_width=True)

# Page title
st.markdown("""
# 
This website allows you to predict Bioactivity towards inhibting the `Human epidermal growth factor receptor 2(HER2) proteins`. HER2 is a member of the epidermal growth factor receptor tyrosine kinase family, a family of receptors implicated in the pathogenesis of different types of cancers. The overexpression of HER2, specifically, is involved in many tumors: breast, gastric, prostate, head and neck, ovarian, and more. Therefore, HER2 became a chief target for anti-carcinogenic therapeutic agents. 

**Credits**
- App built by [DR.Sara Salah]

""")

# Sidebar
with st.sidebar.header('1. Upload your CSV data'):
    uploaded_file = st.sidebar.file_uploader("Upload your input file", type=['txt'])
    st.sidebar.markdown("""
[Example input file](https://github.com/sara-s1/WebSiteApp_C/blob/main/Lapatinib_TykerbH_.txt)
""")

if st.sidebar.button('Predict'):
    load_data = pd.read_table(uploaded_file, sep=' ', header=None)
    load_data.to_csv('molecule.smi', header = False, index = False,encoding='utf-8')

    st.header('**User Input Data**')
    st.write(load_data)

    with st.spinner("Calculating  in progress..."):
        desc_calc()

    # Read in calculated descriptors and display the dataframe
    # st.header('**Calculated molecular descriptors**')
    desc = pd.read_csv('descriptors_output.csv')
    # st.write(desc)
    # st.write(desc.shape)

    # Read descriptor list used in previously built model
    # st.header('**Subset of descriptors from previously built models**')
    Xlist = list(pd.read_csv('descriptor_list.csv').columns)
    desc_subset = desc[Xlist]
    # st.write(desc_subset)
    # st.write(desc_subset.shape)

    # Apply trained model to make prediction on query compounds
    build_model(desc_subset)
else:
    st.info('Upload input data in the sidebar to start!')
