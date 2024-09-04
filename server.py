import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template, redirect, url_for

app = Flask(__name__)

def my_fun(domain, user, password, key):
    # Read existing data from the CSV file
    df = pd.read_csv("my_data.csv")

    # Encrypt the password
    en1 = np.array(list(map(ord, list(password))))
    en1 *= int(key)
    en2 = np.array(list(map(chr, list(en1)))).astype('str')
    en2 = ''.join(en2)

    # Prepare the data to be added
    new_entry = {
        "Domain name": domain,
        "username": user,
        "password": en2
    }

    # Convert the dictionary to a DataFrame and concatenate with the existing data
    df1 = pd.DataFrame(data=new_entry, index=[0])
    df = pd.concat((df, df1), axis=0, ignore_index=True)

    # Save the updated DataFrame back to the CSV file
    df.to_csv("my_data.csv", index=False)

    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/access')
def access():
    return render_template('access.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    # Get the form data directly from the request object
    domain = request.form['domainName']
    key = request.form['keyFactor']

    # Read the CSV file to find the corresponding entry
    df = pd.read_csv("my_data.csv")
    user_entry = df[df['Domain name'] == domain]

    if not user_entry.empty:
        encrypted_password = user_entry.iloc[0]['password']

        # Decrypt the password
        en1 = np.array(list(map(ord, list(encrypted_password))))
        en1 = en1 // int(key)
        decrypted_password = ''.join(map(chr, en1))

        return render_template('details.html', domain=domain, username=user_entry.iloc[0]['username'], password=decrypted_password)
    else:
        return "Authentication failed", 401

@app.route('/register', methods=['POST'])
def register_user():
    # Get the form data
    domain = request.form['domain']
    username = request.form['username']
    password = request.form['password']
    key = request.form['key']

    # Call the my_fun function to save the data
    my_fun(domain, username, password, key)

    return redirect(url_for('index'))

@app.route('/details/<domain>')
def show_details(domain):
    # Fetch the user details based on the domain name
    df = pd.read_csv("my_data.csv")
    user_entry = df[df['Domain name'] == domain]

    if not user_entry.empty:
        username = user_entry.iloc[0]['username']
        password = user_entry.iloc[0]['password']
        return render_template('details.html', domain=domain, username=username, password=password)
    else:
        return "User not found", 404

if __name__ == '__main__':
    # Create a CSV file with the necessary columns if it doesn't exist
    try:
        pd.read_csv("my_data.csv")
    except FileNotFoundError:
        pd.DataFrame(columns=["Domain name", "username", "password"]).to_csv("my_data.csv", index=False)

    app.run(debug=True)
