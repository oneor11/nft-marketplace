import streamlit as st
from multiapp import MultiApp
from apps import buyer, home,creator # import your app modules here

app = MultiApp()

st.markdown("""
# NFT Market Place
This multi-page app is using the [streamlit-multiapps](https://github.com/upraneelnihar/streamlit-multiapps) framework developed by [Praneel Nihar](https://medium.com/@u.praneel.nihar). Also check out his [Medium article](https://medium.com/@u.praneel.nihar/building-multi-page-web-app-using-streamlit-7a40d55fa5b4).
""")

# Add all your application here
app.add_app("Home", home.home)
app.add_app("Creator", creator.creator)
app.add_app("Buyer", buyer.buyer)

# The main app
app.run()

