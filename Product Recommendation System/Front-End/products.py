import streamlit as st
import pickle
import pandas as pd
import requests

# Load the necessary python pickle files
products_dict = pickle.load(open('../Model Development/product_dict.pkl','rb'))
products = pd.DataFrame(products_dict)

customers = pickle.load(open('../Model Development/customers.pkl','rb'))

knn_model = pickle.load(open('../Model Development/knn_model.pkl','rb'))
X_train = pickle.load(open('../Model Development/X_train.pkl','rb'))

def recommend(user_id, num_recommendations=6):
    try:
        user_index = X_train.index.get_loc(user_id)
        distances, indices = knn_model.kneighbors(X_train.iloc[user_index, :].values.reshape(1, -1), n_neighbors=num_recommendations + 1)
    
        recommended_products = []
        for i in range(1, num_recommendations + 1):
            product_id = X_train.columns[indices.flatten()[i]]
            recommended_products.append(product_id)
    
        return recommended_products
    
    except KeyError:
        st.error("User with the selected nickname not found.")
        return []


# Fetch posters from the TMDb database
def fetch_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=ENTER_API_KEY_HERE&language=en-US'.format(movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']


# Streamlit app
st.title("Product Recommendation App")


# Create a dropdown menu with user nicknames
selected_nickname = st.selectbox("Select User's Nickname", customers['NickName'])

if st.button("Get Recommendations"):
    # Find the corresponding CustomerID for the selected nickname
    matching_row = customers[customers['NickName'] == selected_nickname]
    
    if not matching_row.empty:
        user_id = matching_row.iloc[0]['Id']
        
        # Get recommendations for the user
        recommended_product_ids = recommend(user_id)
        
        # Display the recommended product names
        recommended_products = products[products['Id'].isin(recommended_product_ids)]
        st.subheader("Recommended Products:")
        st.table(recommended_products[['Name', 'UnitPrice']])
    else:
        st.error("User with the selected nickname not found.")