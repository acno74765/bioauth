# src/database.py
from concrete import fhe
import sqlite3
import numpy as np
import os
from .preprocessing import load_and_preprocess_image, extract_fingercode_features

def quantize_features(features, scale=1000):
    """Scale and convert floating-point features to integers."""
    quantized_features = np.round(features * scale).astype(np.int32)  # Scale and round to integers
    return quantized_features

def encrypt_features(features):
    """Quantize and encrypt the feature vector using Concrete."""
    # Quantize features to integers
    quantized_features = quantize_features(features)

    # Define the encryption function (example: identity function)
    def encrypt_fn(x):
        return x + 1  # Example logic: Add 1 to input for encryption demonstration
    
    # Compile the encryption function
    compiler = fhe.Compiler(encrypt_fn, {"x": "encrypted"})
    inputset = [(quantized_features,)]
    circuit = compiler.compile(inputset)
    circuit.keygen()

    # Encrypt the quantized feature vector
    encrypted_features = circuit.encrypt(quantized_features)
    print("Features encrypted successfully.")
    return encrypted_features

def create_database(db_name="data/fingerprints.db"):
    """Create an SQLite database and a table for storing fingerprint features."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fingerprints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT NOT NULL,
            features BLOB NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database {db_name} created with table fingerprints.")


# Stored as BLOB and not encrypted
# Using ZAMA concrete library for encryption
def insert_features_into_database(db_name, label, features):
    """Encrypt and insert fingerprint features into the SQLite database."""
    encrypted_features = encrypt_features(features)
    encrypted_blob = encrypted_features.tobytes()
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO fingerprints (label, features)
        VALUES (?, ?)
    ''', (label, encrypted_blob))
    conn.commit()
    conn.close()
    print("Successful insertion into database - encrypted features")


def create_and_populate_database(fingerprint_dir, db_name="data/fingerprints.db"):
    """Create a database and populate it with encrypted fingerprint feature vectors."""
    create_database(db_name)
    for filename in os.listdir(fingerprint_dir):
        if filename.endswith(".bmp") or filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(fingerprint_dir, filename)
            try:
                # Process the fingerprint image
                enhanced_image = load_and_preprocess_image(image_path)
                finger_code_features = extract_fingercode_features(enhanced_image)
                label = os.path.splitext(filename)[0]
                
                # Insert encrypted features into the database
                insert_features_into_database(db_name, label, finger_code_features)
                print(f"Processed {filename} - Encrypted features inserted into the database.")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")


def view_encrypted_data(db_name="data/fingerprints.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT label, features FROM fingerprints")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        print(f"Label: {row[0]}")
        print(f"Encrypted Features (BLOB): {row[1]}")
        print(f"Length of Encrypted Features: {len(row[1])}")



def delete_data_from_database(db_name, label):
    """Delete a fingerprint entry from the SQLite database based on the label."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Delete the entry from the fingerprints table where the label matches
    cursor.execute('DELETE FROM fingerprints WHERE label = ?', (label,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print(f"Entry with label '{label}' deleted from the database.")

    
# def get_features_from_db(db_name):
#     """Retrieve the feature vectors from the database."""
#     conn = sqlite3.connect(db_name)
#     cursor = conn.cursor()
    
#     # Retrieve feature vectors
#     cursor.execute("SELECT label, features FROM fingerprints")
#     rows = cursor.fetchall()
#     conn.close()
    
#     # Convert features back from binary format
#     feature_vectors = []
#     for label, features_blob in rows:
#         features = np.frombuffer(features_blob, dtype=np.float32)
#         feature_vectors.append((label, features))
#     print("Sucesful retreival of features from the database\n")
#     return feature_vectors


#def get_features_from_database(db_name, label):
#     """Retrieve fingerprint features from the SQLite database based on the label."""
#     conn = sqlite3.connect(db_name)
#     cursor = conn.cursor()

#     # Query the database
#     cursor.execute('SELECT features FROM fingerprints WHERE label = ?', (label,))
#     result = cursor.fetchone()

#     # Close the connection
#     conn.close()

#     if result:
#         # Convert the binary data back to a NumPy array
#         features = np.frombuffer(result[0], dtype=np.float32)
#         # Ensure the features are 640-dimensional
#         if len(features) != 640:
#             features = np.pad(features, (0, 640 - len(features)), 'constant') if len(features) < 640 else features[:640]
#         return features
#     else:
#         print(f"No entry found for label: {label}")
#         return None                