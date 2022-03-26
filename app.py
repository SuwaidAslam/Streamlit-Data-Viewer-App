import streamlit as st
import pandas as pd
import numpy as np
import streamlit_authenticator as stauth
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image

if 'logoImg' not in st.session_state:
    st.session_state['logoImg'] = Image.open('if-logo.png')
# change actual name for the users
names = ['user-1', 'user-2', 'user-3', 'user-4', 'user-5', 'user-6', 'user-7', 
        'user-8', 'user-9', 'user-10']

# change user name for the users
usernames = ['user-1', 'user-2', 'user-3', 'user-4', 'user-5', 'user-6', 'user-7', 
            'user-8', 'user-9', 'user-10']

# change password for the users
passwords = ['password-1', 'password-2', 'password-3', 'password-4', 'password-5', 'password-6', 'password-7',
            'password-8', 'password-9', 'password-10']

st.set_page_config(
    page_title="ZDL Data Viewer",
    initial_sidebar_state="expanded",
    layout="wide"
)

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def getData():
        if 'df' not in st.session_state:
            df = pd.read_csv('my_csv250322_1.csv',sep=";")
            df  = df.iloc[: , 2:]
            df = df.dropna()
            df = df.reset_index(drop=True)
            df["MEASUREMENT_VALUE"] = df["MEASUREMENT_VALUE"].astype(str).str.split(".",2)
            df["ALARM_HIGH"] = df["ALARM_HIGH"].astype(str).str.split(".", 2)
            df["DANGER_HIGH"] = df["DANGER_HIGH"].astype(str).str.split(".", 2)
            df['DIRECTION'] = df['DIRECTION'].str[1:]
            for i in range(len(df)):
                v1 = df.loc[i, "MEASUREMENT_VALUE"]
                if(len(v1) > 2):
                    df.loc[i, "MEASUREMENT_VALUE"] = float(v1[0] + "." + v1[1] + v1[2])
                else:
                    df.loc[i, "MEASUREMENT_VALUE"] = float(v1[0] + "." + v1[1])
                v2 = df.loc[i, "ALARM_HIGH"]
                if(len(v2) > 2):
                    df.loc[i, "ALARM_HIGH"] = float(v2[0] + "." + v2[1] + v2[2])
                else:
                    df.loc[i, "ALARM_HIGH"] = float(v2[0] + "." + v2[1])
                v3 = df.loc[i, "DANGER_HIGH"]
                if(len(v3) > 2 ):
                    df.loc[i, "DANGER_HIGH"] = float(v3[0] + "." + v3[1] + v3[2])
                else:
                    df.loc[i, "DANGER_HIGH"] = float(v3[0] + "." + v3[1])
        
            df[['MEASUREMENT_VALUE','ALARM_HIGH', 'DANGER_HIGH']] = df[['MEASUREMENT_VALUE','ALARM_HIGH', 
                'DANGER_HIGH']].astype(float, errors = 'raise')
            st.session_state['df'] = df
            return st.session_state['df']
        else:
            return st.session_state['df']

# Detailed View Page Function
def detailedView():
    df = getData()
    customers = df.naam.unique()
    customerSelectBoxVal = st.sidebar.selectbox('Customers', customers)
    specificCustomer =  df.loc[df['naam'] == customerSelectBoxVal]

    #get unique objects of a single customer
    objects = specificCustomer['if'].unique()
    objects = np.insert(objects, 0, '')
    objectSelectBoxVal = st.sidebar.selectbox('Objects', objects, index=0)
    finalDf = specificCustomer.loc[specificCustomer['if'] == objectSelectBoxVal]
    finalDf = finalDf.filter(['if','IF_NUMBER','klantFK','naam','PART', 'NAME', 'CINEMATIC_PATH', 'DISPLACEMENT','DIRECTION', 'DATE_MEASUREMENT', 'MEASUREMENT_VALUE', 'DANGER_HIGH', 'ALARM_HIGH'])
    displacement = finalDf.groupby(['DISPLACEMENT','NAME','PART'])

    if(objectSelectBoxVal != ''):
        subPlotsCounter = 0
        subPlotTitles = []
        for df in displacement:
            subPlotsCounter +=1
            subPlotTitles.append("Plot_"+str(subPlotsCounter))
        st.header('Correlation:')
        subPlot_fig = make_subplots(rows=4, cols=2, start_cell="top-left",
        vertical_spacing= 0.14,
        subplot_titles=tuple(subPlotTitles)
        )
        row_ = 1 # rows in subplot fig
        col_ = 1 # columns in subplot fig
        subPlotCount = 1 # count number of plots
        titles = []
        legendVisibility = True
        for derivative, df in displacement:
            if col_ > 2:
                row_+=1
                col_ = 1
            if subPlotCount > 1:
                legendVisibility = False
            df = df.reset_index()
            df["DATE_MEASUREMENT"] = pd.to_datetime(df["DATE_MEASUREMENT"])
            df = df.filter(['IF_NUMBER','PART', 'NAME','DIRECTION','DISPLACEMENT', 'DATE_MEASUREMENT', 'MEASUREMENT_VALUE','DANGER_HIGH','ALARM_HIGH'])
            
            uniqueDirections = df.DIRECTION.unique()
            direc1Data =  df.loc[df['DIRECTION'] == uniqueDirections[0]]
            direc2Data =  df.loc[df['DIRECTION'] == uniqueDirections[1]]
            direc3Data =  df.loc[df['DIRECTION'] == uniqueDirections[2]]

            alertHigh = direc1Data["ALARM_HIGH"]
            dangerHigh = direc1Data["DANGER_HIGH"]

            subPlot_fig.add_trace(go.Scatter(
            x = direc3Data["DATE_MEASUREMENT"],
            y = dangerHigh,
            name = "Danger High",
            mode ="lines",
            line = dict(shape = 'linear', color = 'red', dash = 'dot'),
            showlegend=legendVisibility,
            ),
            row=row_, col=col_)

            subPlot_fig.add_trace(go.Scatter(
            x = direc3Data["DATE_MEASUREMENT"],
            y = alertHigh,
            name = "Alert High",
            mode ="lines",
            line = dict(shape = 'linear', color = 'orange', dash = 'dot'),
            showlegend=legendVisibility,
            ),
            row=row_, col=col_)

            subPlot_fig.add_trace(go.Scatter(
            x= direc1Data["DATE_MEASUREMENT"],
            y= direc1Data["MEASUREMENT_VALUE"],
            name= direc1Data['DIRECTION'].values[0],
            line = dict(shape = 'linear', color = 'lightblue'),
            showlegend=legendVisibility,
            ),
            row=row_, col=col_)

            subPlot_fig.add_trace(go.Scatter(
            x= direc2Data["DATE_MEASUREMENT"],
            y= direc2Data["MEASUREMENT_VALUE"],
            name= direc2Data['DIRECTION'].values[0],
            line = dict(shape = 'linear', color = 'lightcoral'),
            showlegend=legendVisibility,
            ),
            row=row_, col=col_) 

            subPlot_fig.add_trace(go.Scatter(
            x= direc3Data["DATE_MEASUREMENT"],
            y= direc3Data["MEASUREMENT_VALUE"],
            name= direc3Data['DIRECTION'].values[0],
            line = dict(shape = 'linear', color = 'lightgreen'),
            showlegend=legendVisibility,
            ),
            row=row_, col=col_)

            subPlot_fig.update_layout(
                height=800,
                width =800,
                font=dict(
                    family="monospace",
                    size= 12,
                    color="RebeccaPurple"
                )
            )
            col_ += 1
            titles.append(df['IF_NUMBER'].iloc[0] + ':   ' + df['PART'].iloc[0] + ' - '+df['NAME'].iloc[0] + ' - '+ df['DISPLACEMENT'].iloc[0])
            subPlotCount += 1
        # Add subtitles to sub graphs
        subTitle = dict()
        for i, title in enumerate(titles):
            subTitle.update({subPlotTitles[i]: title})
        subPlot_fig.for_each_annotation(lambda a: a.update(text = subTitle[a.text]))
        subPlot_fig.update_annotations(font=dict(family="Helvetica", size=8))
        st.plotly_chart(subPlot_fig)

        showIndividualGraphs = st.sidebar.checkbox('Show Individual Graphs')
        if showIndividualGraphs:
            st.header('Individual Graphs:')
            for derivative, df in displacement:
                fig_ob = go.Figure()
                df = df.reset_index()
                df["DATE_MEASUREMENT"] = pd.to_datetime(df["DATE_MEASUREMENT"])
                df = df.filter(['IF_NUMBER','PART', 'NAME','DIRECTION','DISPLACEMENT', 'DATE_MEASUREMENT', 'MEASUREMENT_VALUE','DANGER_HIGH','ALARM_HIGH'])

                uniqueDirections = df.DIRECTION.unique()
                direc1Data =  df.loc[df['DIRECTION'] == uniqueDirections[0]]
                direc2Data =  df.loc[df['DIRECTION'] == uniqueDirections[1]]
                direc3Data =  df.loc[df['DIRECTION'] == uniqueDirections[2]]
                    
                alertHigh = direc1Data["ALARM_HIGH"]
                dangerHigh = direc1Data["DANGER_HIGH"]

                fig_ob.add_trace(go.Scatter(
                x = direc3Data["DATE_MEASUREMENT"],
                y = dangerHigh,
                name = "Danger High",
                mode ="lines",
                line = dict(shape = 'linear', color = 'red', dash = 'dot')
                ))

                fig_ob.add_trace(go.Scatter(
                x = direc3Data["DATE_MEASUREMENT"],
                y = alertHigh,
                name = "Alert High",
                mode ="lines",
                line = dict(shape = 'linear', color = 'orange', dash = 'dot')
                ))

                fig_ob.add_trace(go.Scatter(
                x= direc1Data["DATE_MEASUREMENT"],
                y= direc1Data["MEASUREMENT_VALUE"],
                name= direc1Data['DIRECTION'].values[0]
                ))

                fig_ob.add_trace(go.Scatter(
                x= direc2Data["DATE_MEASUREMENT"],
                y= direc2Data["MEASUREMENT_VALUE"],
                name= direc2Data['DIRECTION'].values[0]
                ))

                fig_ob.add_trace(go.Scatter(
                x= direc3Data["DATE_MEASUREMENT"],
                y= direc3Data["MEASUREMENT_VALUE"],
                name= direc3Data['DIRECTION'].values[0],
                ))

                fig_ob.update_layout(
                    title= df['IF_NUMBER'].iloc[0] + ':   ' + df['PART'].iloc[0] + ' - '+df['NAME'].iloc[0] + ' - '+ df['DISPLACEMENT'].iloc[0], title_x=0.5,
                    xaxis_title= "DATE_MEASUREMENT",
                    yaxis_title= "VALUES",
                    font=dict(
                        family="monospace",
                        size= 12,
                        color="RebeccaPurple"
                    )
                )
                st.plotly_chart(fig_ob)
                st.dataframe(df)

 # Overview Page Function 
def overview():
    st.header("Analytics Overview")
    cols = st.columns(3)

    @st.cache
    def getCounts():
        df = getData()
        customersCount = df.naam.nunique()
        objectsCount = df['if'].nunique()
        measurementsCount = df.loc[df['DIRECTION'] == 'Ax']['DIRECTION'].count()
        totalObjects = df['if'].unique()
        # How many objects in green (Under Alarm High)
        # Under the ALARM_HIGH level
        greenObjects = 0
        # Above the ALARM_HIGH level and below DANGER_HIGH level.
        orangeObjects = 0
        #above the DANGER_HIGH level.
        redObjects = 0
        satusDf = pd.DataFrame()
        for object in totalObjects:
            singleObjDf = df.loc[df['if'] == object]
            maxMeasurmentValue = singleObjDf['MEASUREMENT_VALUE'].max()
            if(maxMeasurmentValue < singleObjDf['ALARM_HIGH'].max()):
                singleObjDf['Status'] = 'green'
                satusDf = satusDf.append(singleObjDf)
                greenObjects+=1
            elif(maxMeasurmentValue >= singleObjDf['ALARM_HIGH'].max() and maxMeasurmentValue < singleObjDf['DANGER_HIGH'].max()):
                singleObjDf['Status'] = 'orange'
                satusDf = satusDf.append(singleObjDf)
                orangeObjects+=1
            elif(maxMeasurmentValue >= singleObjDf['DANGER_HIGH'].max()):
                singleObjDf['Status'] = 'red'
                satusDf = satusDf.append(singleObjDf)
                redObjects+=1
        return customersCount, objectsCount, measurementsCount, greenObjects, orangeObjects, redObjects, satusDf
        
    customersCount, objectsCount, measurementsCount, greenObjects, orangeObjects, redObjects, satusDf = getCounts()
    
    # How many customers
    customersCountFig = go.Figure()
    customersCountFig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = customersCount,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Customers"},
        gauge = {'bar': {'color': "gray"}}
        ))
    customersCountFig.update_layout(
    margin=dict(l=3, r=18, t=0, b=0),
    )
    cols[0].plotly_chart(customersCountFig,use_container_width=True)

    # How many Objects
    objectsCountFig = go.Figure()
    objectsCountFig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = objectsCount,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Objects"},
        gauge = {'bar': {'color': "gray"}}
        ))
    objectsCountFig.update_layout(
    margin=dict(l=2, r=2, t=0, b=0),
    )
    cols[1].plotly_chart(objectsCountFig, use_container_width=True)

    # How many measurements
    measurementsCountFig = go.Figure()
    measurementsCountFig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = measurementsCount,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Measurements"},
        gauge = {'bar': {'color': "gray"}}
        ))
    measurementsCountFig.update_layout(
    margin=dict(l=8, r=25, t=0, b=0),
    )
    cols[2].plotly_chart(measurementsCountFig, use_container_width=True)

     # How many objects below Alarm High
    greenCountFig = go.Figure()
    greenCountFig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = greenObjects,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Objects Green"},
        gauge = {'bar': {'color': "Green"}}
        ))
    greenCountFig.update_layout(
    margin=dict(l=3, r=18, t=0, b=0),
    )
    cols[0].plotly_chart(greenCountFig,use_container_width=True)

    # How many objects above Alarm High and below Danger High
    orangeCountFig = go.Figure()
    orangeCountFig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = orangeObjects,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Objects Orange"},
        gauge = {'bar': {'color': "Orange"}}
        ))
    orangeCountFig.update_layout(
    margin=dict(l=2, r=4, t=0, b=0),
    )
    cols[1].plotly_chart(orangeCountFig, use_container_width=True)

    # How many objects above Danger High
    redCountFig = go.Figure()
    redCountFig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = redObjects,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Objects Red"},
        gauge = {'bar': {'color': "Red"}}
        ))
    redCountFig.update_layout(
    margin=dict(l=8, r=25, t=0, b=0),
    )
    cols[2].plotly_chart(redCountFig, use_container_width=True)
    # Partcular Object table
    statusSelector = st.sidebar.selectbox('Object Status', ['Green', 'Orange', 'Red'])
    objectsStatusWise = satusDf[satusDf['Status'] == statusSelector.lower()]
    uniqueObjects = objectsStatusWise['if'].unique()
    objectsSelector = st.sidebar.selectbox('Objects', uniqueObjects)
    st.dataframe(objectsStatusWise.loc[objectsStatusWise['if'] == objectsSelector])

def main():
    logPlaceholder = st.empty()
    titlePlaceholder = st.empty()
    logPlaceholder.image(st.session_state['logoImg'], width=350)
    original_title = '<p style="font-family:Monospace; color:Gray; font-size: 25px;">ZDL Data Viewer</p>'
    titlePlaceholder.markdown(original_title, unsafe_allow_html=True)
    hashed_passwords = stauth.hasher(passwords).generate()
    authenticator = stauth.authenticate(names,usernames,hashed_passwords,
        'authenticator','auth',cookie_expiry_days=0)
    name, authentication_status = authenticator.login('Login','main')
    if authentication_status:
        logPlaceholder.empty()
        titlePlaceholder.empty()
        st.sidebar.image(st.session_state['logoImg'] , width=215)
        pageSelection = st.sidebar.selectbox("Select Page", ["Overview", "Detailed View"])
        if pageSelection == "Overview":
            overview()
        else:
            detailedView()
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')

if __name__ == '__main__':
    main()
