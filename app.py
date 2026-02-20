import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import base64

def set_background(image_file):
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()

    bg_style = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """

    st.markdown(bg_style, unsafe_allow_html=True)

set_background("bg.jpg") 

st.markdown("""
<style>
/* Sidebar background */
section[data-testid="stSidebar"] {
    background-color: #1C4136;
}

/* Sidebar text color */
section[data-testid="stSidebar"] * {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8") #converting bytestream to string

    df = preprocessor.preprocess(data)

    #fetch unique users
    user_list = df["users"].unique().tolist()
    user_list.remove("group_notification")
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):
        num_msgs, num_words, num_media, num_links = helper.fetch_stats(selected_user, df)

        st.title("Message Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.subheader("Total Messages")
            st.title(num_msgs)
        with col2:
            st.subheader("Total Words")
            st.title(num_words)
        with col3:
            st.subheader("Total Media Shared")
            st.title(num_media)
        with col4:
            st.subheader("Total Links Shared")
            st.title(num_links)

        #timeline
        st.title("Timeline")
        col1, col2 = st.columns(2)

        with col1:
            #monthly timeline
            st.subheader("Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax =  plt.subplots(figsize=(6,4))
            ax.plot(timeline["time"], timeline["msgs"])
            plt.xticks(rotation = "vertical")
            st.pyplot(fig)

        with col2:
            # daily timeline
            st.subheader("Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots(figsize=(6,5))
            ax.plot(daily_timeline['only_date'], daily_timeline['msgs'])
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        #group evel analysis
        #1. finding most active users in group
        if selected_user == "Overall":
            st.title("Most Active Users")
            x, new_df = helper.fetch_top_users(df)
            fig, ax = plt.subplots()
            
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("User Message Percentage")
                st.dataframe(new_df)

            with col2:
                st.subheader("Bar Graph Representation")
                ax.bar(x.index, x.values, color = "green")
                plt.xticks(rotation = "vertical")
                st.pyplot(fig)

        #word analysis
        st.title("Word Analysis")
        col1, col2 = st.columns(2)

        with col1:
            #wordcloud
            st.subheader("WordCloud ")
            df_wc = helper.wordcloud(selected_user, df)
            if df_wc is not None:
                st.image(df_wc.to_array(), width=400)
            else:
                st.write("No words available to generate WordCloud.")
        with col2:
            #most common words
            st.subheader('Most commmon words')
            most_common_df = helper.most_common_words(selected_user,df)
            if not most_common_df.empty:
                fig,ax = plt.subplots()
                ax.barh(most_common_df[0],most_common_df[1])
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            else:
                st.write("No words found for this user.")

        #emoji analysis
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        col1,col2 = st.columns(2)

        with col1:
            st.subheader("Emoji Count")
            st.dataframe(emoji_df)
        with col2:
            st.subheader("Pie Chart Representation")
            if not emoji_df.empty:   
                fig, ax = plt.subplots()
                ax.pie(emoji_df["Count"].head(), labels=emoji_df["Emoji"].head(), autopct="%0.2f%%")
                st.pyplot(fig)
            else:

                st.write("No emojis found for this user.") 
