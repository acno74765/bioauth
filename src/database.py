# src/database.py
from concrete import fhe
import sqlite3
import numpy as np
import os
from .preprocessing import load_and_preprocess_image, extract_fingercode_features

def encrypt_features(features):
    """Encrypt the feature vector using Concrete."""
    # Compile an encryption function
    def encrypt_fn(x):
        return x  # Placeholder; replace with actual homomorphic encryption logic
    
    compiler = fhe.Compiler(encrypt_fn, {"x": "encrypted"})
    inputset = [(features,)]
    circuit = compiler.compile(inputset)
    circuit.keygen()
    
    encrypted_features = circuit.encrypt(features)
    return encrypted_features

def get_features_from_db(db_name):
    """Retrieve the feature vectors from the database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Retrieve feature vectors
    cursor.execute("SELECT label, features FROM fingerprints")
    rows = cursor.fetchall()
    conn.close()
    
    # Convert features back from binary format
    feature_vectors = []
    for label, features_blob in rows:
        features = np.frombuffer(features_blob, dtype=np.float32)
        feature_vectors.append((label, features))
    
    return feature_vectors

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
    """Insert fingerprint features into the SQLite database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    features_blob = features.tobytes()
    cursor.execute('''
        INSERT INTO fingerprints (label, features)
        VALUES (?, ?)
    ''', (label, features_blob))
    conn.commit()
    conn.close()

def create_and_populate_database(fingerprint_dir, db_name="data/fingerprints.db"):
    """Create a database and populate it with fingerprint feature vectors."""
    create_database(db_name)
    for filename in os.listdir(fingerprint_dir):
        if filename.endswith(".bmp") or filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(fingerprint_dir, filename)
            try:
                enhanced_image = load_and_preprocess_image(image_path)
                finger_code_features = extract_fingercode_features(enhanced_image)
                label = os.path.splitext(filename)[0]
                insert_features_into_database(db_name, label, finger_code_features)
                feature_vectors = get_features_from_db(db_name)
                for label, features in feature_vectors:
                    encrypted_features = encrypt_features(features)
                    insert_features_into_database(db_name, label, encrypted_features)  # Store encrypted features back
                print("Encrypted features have been stored in the database.")
                print(f"Processed {filename} - Features inserted into the database.")
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

def get_features_from_database(db_name, label):
    """Retrieve fingerprint features from the SQLite database based on the label."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Query the database
    cursor.execute('SELECT features FROM fingerprints WHERE label = ?', (label,))
    result = cursor.fetchone()

    # Close the connection
    conn.close()

    if result:
        # Convert the binary data back to a NumPy array
        features = np.frombuffer(result[0], dtype=np.float32)
        # Ensure the features are 640-dimensional
        if len(features) != 640:
            features = np.pad(features, (0, 640 - len(features)), 'constant') if len(features) < 640 else features[:640]
        return features
    else:
        print(f"No entry found for label: {label}")
        return None                

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