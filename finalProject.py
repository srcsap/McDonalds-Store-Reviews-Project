#Name: Sam Saperstein
#CS230: Section 4
#Data: McDonalds Store Reviews
#URL:

#Description:
#This program

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk
from wordcloud import WordCloud
def loadData():#used py3
    try:
        df=pd.read_csv("MCDData.csv")
    except:
        try:
            df=pd.read_csv("MCDData.csv",encoding="latin1")

        except:
            print("unable to load data")
            df = pd.DataFrame()
    return df
def cleanData(df): #used da1
    df=df[df.store_address.apply(lambda x:", " in x)]

    df["rating"] = df["rating"].apply(lambda x: x[0]).astype(int)
    df["store_address_split"] = df["store_address"].apply(lambda x: x.split(", "))
    df["city"]=df.store_address_split.apply(lambda x:x[-3])#da9
    df["state"]=df.store_address_split.apply(lambda x:x[-2][:2])
    df=df.drop("store_address_split",axis=1)#da7
    return df
def filterData(df):
    if state != "all":
        df = df[df.state==state]
    if city != "all":
        df = df[df.city == city]
    df=df[(df.rating >= min_rating) & (df.rating<= max_rating)]#da5
    if keyword != "":

        df = df[df.review.apply(lambda x: keyword.lower() in x.lower())]
    return df
def stateStats(df, state):#uses py2
    statedf = df.query("state==@state")#da4
    numRev = len(statedf)
    avgRating = statedf.rating.mean()
    return numRev,avgRating
def keyWordCounts(df,excluded_words=[]):#uses py5 and py1
    keywords = {}
    for i,row in df.iterrows():#da8
        for word in row.review.split():
            word = word.replace(",","").replace(".","").replace("?","").replace("!","").lower()
            if word not in excluded_words:
                keywords[word]=keywords.get(word,0)+1
    return keywords




df= loadData()
df=cleanData(df)

st.set_page_config(page_title="MCD Rev Data",layout="wide")

st.sidebar.title ("Filters")
state = st.sidebar.selectbox ("State",options = ["all"] + list(df.state.unique()))
city = st.sidebar.selectbox ("City",options = ["all"] + list(df.query("state == @state").city.unique())  if state != "all" else ["all"] + list(df.city.unique()))

min_rating = st.sidebar.slider("Min Rating", 1,5,1)#st4
max_rating = st.sidebar.slider("Max Rating", 1,5,5)
keyword = st.text_input("Must contain (optional)")
st.sidebar.markdown("Customize your view from the left panel")
filtered_df = filterData(df)
st.title("MCD Rev Data")
if city != "all" and state != "all":
    st.write(f"Showing results for {city}, {state}")
elif city != "all":
    st.write(f"Showing results for {city}")
elif state != "all":
    st.write(f"Showing results for {state}")
else:
    st.write("Showing all data")

st.subheader("Top Cities by Avg Rating")#chart 1
if city == "all":
    top_cities = filtered_df.groupby("city")["rating"].mean().sort_values(ascending=False)
    fig1, ax1 = plt.subplots()
    top_cities.plot(kind = "barh", color = "yellow", ax = ax1)
    ax1.set_xlabel("Average Rating")
    ax1.set_title("Top Cities")
    st.pyplot(fig1)
else:
    st.write("Only one city selected")

st.subheader("Common Words")
keywords = keyWordCounts(filtered_df)
wc = WordCloud(width = 800, height = 400, background_color = "gray").generate_from_frequencies(keywords)
figWC, axWC = plt.subplots()
axWC.imshow(wc,interpolation="bilinear")
axWC.axis("off")
st.pyplot(figWC)


st.subheader("Common Words (without stopwords)")
keywords = keyWordCounts(filtered_df, ["the", "to", "is", "and", "a", "in", "of", "for", "on", "it"])
wc = WordCloud(width = 800, height = 400, background_color = "gray").generate_from_frequencies(keywords)
figWC, axWC = plt.subplots()
axWC.imshow(wc,interpolation="bilinear")
axWC.axis("off")
st.pyplot(figWC)

st.subheader("Map of Select Reviews")
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=filtered_df["latitude"].mean(),
        longitude=filtered_df["longitude"].mean(),
        zoom=3,
        pitch=45,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position='[longitude, latitude]',
            get_fill_color='[255 - rating * 40,rating * 40,100]',
            get_radius=8000,
            pickable=True,
        ),
    ],
    tooltip={"text": "Rating: {rating}\nReview: {review}"}
))


st.subheader("Rating Distribution by State")
if state != "all":
    fig2, ax2 = plt.subplots()
    sns.histplot(filtered_df["rating"], bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5], kde=False, ax=ax2, color="#ffb347")
    ax2.set_title(f"Rating Distribution in {state}")
    ax2.set_xlabel("Rating")
    ax2.set_ylabel("Number of Reviews")
    ax2.set_xticks([1,2,3,4,5])
    st.pyplot(fig2)
    num_reviews,average_rating = stateStats(df,state)
    st.write(f"{num_reviews:,} reviews with an average rating of {average_rating:2f} in {state}")
else:
    st.write("Must select a state")








