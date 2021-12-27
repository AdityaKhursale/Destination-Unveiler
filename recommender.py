# import libriaries
import sqlite3
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import time
from sklearn.metrics.pairwise import cosine_similarity
from item_collector_and_data_organizer import fetchInfo

import hashlib


def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()


def check_hashes(password, hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False


conn = sqlite3.connect('data.db')
c = conn.cursor()


def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username, password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',
	          (username, password))
	conn.commit()


def login_user(username, password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',
	          (username, password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data

# import the data and create revelent dataframes


def load():
    df = pd.read_csv('city_ranking.csv')
    data = df.set_index('city'). iloc[:, 1:-1]
    scores = df.set_index('city'). iloc[:, 1:-1].round().astype(int)
    location = []
    for index, city, country in df[["city", "country"]].sort_values("country").itertuples():
        new = f'{city}, {country}'
        location.append(new)
    return df, data, scores, location

# Calculate the cosine-similarity


def find_similarity(column, user, number, scores, city):
    if city == 'Others' or city == 'Baltimore':
        new_df = scores[column]
    else:
        locate = city.split(',')
        new_df = scores[scores.index != locate[0]][column]
    value = []
    for index, city in enumerate(new_df.index):
        city_old = new_df.loc[city].values.reshape(-1, number)
        user = user.reshape(-1, number)
        score = cosine_similarity(city_old, user)
        value.append(score)
    similarity = pd.Series(value, index=new_df.index)
    city_similar = similarity.sort_values(
        ascending=False).astype(float).idxmax()
    # message = f'Based on your aggregate preferences and ratings, {city_similar} is the top recommended city to move/travel to.'
    return city_similar

# Get more info about the recommended city


def final_answer(df, word, data):
    title = f'About {word}'
    subtitle = 'City Ranking in terms of Business, essentials, Openness and recreation scores(over 10.0)'
    country = df.loc[df['city'] == word, 'country'].iloc[0]
    if word in df['city'].head().values:
        response = "It is actually one of the top 5 cities that has piqued millennials' interests."
    elif word in df['city'].head(10).values:
        response = "It is actually one of the top 10 cities that has piqued millennials' interests."
    elif word in df['city'].tail(5).values:
        response = "It is actually one of the least 5 cities that has piqued millennials' interests."
    else:
        response = ""

    ranking = list(zip(list(data.loc[word].index), data.loc[word]))
    breakdown = pd.DataFrame(ranking, columns=['Category', 'Score'])
    breakdown['Score'] = breakdown['Score'].round(1)

    return title, country, subtitle, response, breakdown

# The app controller


def main():
    st.title('Destination Unveiler')
    # st.write(intro)
    # image= Image.open('unsplash2.jpg')
    # st.image(image, use_column_width=True)

    menu = ["Home", "Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")

    elif choice == "Login":
        st.subheader("Login Section")

        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.checkbox("Login"):
			# if password == '12345'
            create_usertable()
            hashed_pswd = make_hashes(password)
            result = login_user(username,check_hashes(password,hashed_pswd))

            if result:
                st.success("Logged In as {}".format(username))
#                task = st.selectbox("Task",["Add Post","Analytics","Profiles"])
#                if task == "Add Post":
#                    st.subheader("Add Your Post")
#
#                elif task == "Analytics":
#                    st.subheader("Analytics")
#                elif task == "Profiles":
#                    st.subheader("User Profiles")
#                    user_result = view_all_users()
#                    clean_db = pd.DataFrame(user_result,columns=["Username","Password"])
#                    st.dataframe(clean_db)
            else:
                st.warning("Incorrect Username/Password")
    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password",type='password')
        if st.button("Signup"):
            create_usertable()
            add_userdata(new_user,make_hashes(new_password))
            st.success("You have successfully created a valid Account")
            st.info("Go to Login Menu to login")

    html_temp = """
    <br>
    """
    st.markdown(html_temp, unsafe_allow_html=True)

    df, data,scores, location = load()
    available_preferences = {
        "Employment Score": "Employability",
        "Startup Score": "Startups",
        "Tourism Score": "Tourism",
        "Housing Score": "Housing",
        "Food Ranking": "Food",
        "Transport Score": "Public Transport",
        "Health Rank": "Public Health",
        "Internet Speed Score": "Internet",
        "University Score": "Universities",
        "Access to Contraceptive Score": "Contraception",
        "Gender Equality Score": "Gender Equality",
        "Immigration Tolerence": "Immigration Tolerence",
        "Personal Freedom and Choice": "Freedom",
        "LGBT friendly Score": "LGBTQ Friendliness",
        "Nightlife Score": "Nightlife",
        "Beer Ranking": "Beer",
        "Festival Ranking": "Festivals"
    }
    scores = scores.rename(columns=available_preferences)
    location.append('Others')
    location.append('Baltimore, United States')
    city = st.selectbox("Location of Residence", location)
    preference = st.multiselect("Choose features most important to you",scores.columns)
    if st.checkbox("Rate the features"):
        levels = []
        for i in range(len(preference)):
            levels.append(st.slider(preference[i], 1, 10))
        if st.button("Recommend", key="hi"):
            user = np.array(levels)
            column = preference
            number = len(preference)
            city_similar = find_similarity(column, user, number,scores,city)
            with st.spinner("Analyzing..."):
                city_info = fetchInfo([city_similar], 'en')
                time.sleep(1)
            st.text(f'\n\n\n')
            # st.markdown('--------------------------------------------**Recommendation**--------------------------------------------')
            st.text(f'\n\n\n\n\n\n')
            st.header(f'**{city_similar}**')
            title, country , subtitle, response, breakdown = final_answer(df, city_similar, data)
            st.text(f'\n\n\n\n\n\n')
            # st.markdown(f'----------------------------------------------**{title}**---------------------------------------------')
            st.write(f'**Country:** {country}')
            st.text(f'\n\n\n')
            
            image = Image.open(city_info["cityImage"])
            st.image(image, use_column_width=True)
            st.text(f'\n\n\n')
            
            # start = False
            for key, val in city_info.items():
                if key == "cityImage":
                    continue
                if key == "Wikipedia Summary":
                    st.markdown(f'**{key}:**')
                    st.text(f'{val}')
                elif key == "Interesting Places":
                    st.markdown(f'**{key}:**')
                    for v in val:
                        st.text(f'{v}')
                elif key == "Wikipedia Url" or key == "Plan Your Trip At":
                    st.markdown(f'**{key}:** {val}')
                else:
                    st.write(f'**{key}:**')
                    st.write(f'{val}')
            st.table(breakdown.style.format({'Score':'{:17,.1f}'}).background_gradient(cmap='Blues').set_properties(subset=['Score'], **{'width': '250px'}))


    # the end
    st.header("Rate Recommendation")
    x = st.slider('How we performed?',1,5)
    if x==1:
        st.markdown(":star:")
    if x==2:
        st.markdown(":star::star:")
    if x==3:
        st.markdown(":star::star::star:")
    if x==4:
        st.markdown(":star::star::star::star:")
    if x==5:
        st.markdown(":star::star::star::star::star:")
    if st.button("Submit"):
        st.empty()


if __name__ == "__main__":
    main()
