import streamlit as st
from multiapp import MultiApp
from apps import buyer, home,creator # import your app modules here

app = MultiApp()


app.add_app("Home", home.home)
app.add_app("Creator", creator.creator)
app.add_app("Buyer", buyer.buyer)

# The main app
app.run()

