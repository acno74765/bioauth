# src/database.py
from concrete import fhe
import sqlite3
import numpy as np
import os
from .preprocessing import load_and_preprocess_image, extract_fingercode_features

def quantize_features(features, max_value=127):
    """Scale and convert floating-point features to integers within a safe range."""
    # Determine dynamic scale factor to fit max_value
    scale = max_value / np.max(np.abs(features)) if np.max(np.abs(features)) > 0 else 1
    quantized_features = np.clip(np.round(features * scale), 0, max_value).astype(np.uint7)
    print(f"Dynamic Scale Factor: {scale}")
    return quantized_features


def encrypt_features(features, circuit):
    """Quantize and encrypt the feature vector using the provided Concrete circuit."""
    quantized_features = quantize_features(features)
    print(f"Quantized Features (dtype: {quantized_features.dtype}): {quantized_features[:10]}...")
    encrypted_value = circuit.encrypt(quantized_features)
    encrypted_bytes = encrypted_value.serialize()
    print("Features encrypted successfully.")
    return encrypted_bytes


def get_encryption_circuit():
    def encrypt_fn(x):
        return x + 1  # Example encryption logic, modify as needed
    
    compiler = fhe.Compiler(encrypt_fn, {"x": "encrypted"})
    inputset = [(np.random.randint(0, 127, size=640).astype(np.uint7),)] 
    circuit = compiler.compile(inputset)
    return circuit

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
def insert_features_into_database(db_name, label, features, circuit):
    """Insert encrypted fingerprint features into the SQLite database using the provided circuit."""
    if features is None:
        print(f"Error: Feature vector for {label} is None. Skipping insertion.")
        return
    
    # Encrypt and serialize the features using the same circuit
    encrypted_features = encrypt_features(features, circuit)
    
    # Insert the serialized encrypted features into the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO fingerprints (label, features)
        VALUES (?, ?)
    ''', (label, encrypted_features))
    conn.commit()
    conn.close()
    print(f"Successful insertion for {label} into the database.")




def create_and_populate_database(fingerprint_dir, db_name="data/fingerprints.db"):
    """Create a database and populate it with fingerprint feature vectors using a single circuit."""
    # Generate the circuit once
    circuit = get_encryption_circuit()
    create_database(db_name)

    for filename in os.listdir(fingerprint_dir):
        if filename.endswith((".bmp", ".jpg", ".png")):
            image_path = os.path.join(fingerprint_dir, filename)
            try:
                enhanced_image = load_and_preprocess_image(image_path)
                if enhanced_image is None:
                    print(f"Skipping {filename}: Failed to process image.")
                    continue
                
                finger_code_features = extract_fingercode_features(enhanced_image)
                if finger_code_features is None:
                    print(f"Skipping {filename}: Failed to extract features.")
                    continue

                label = os.path.splitext(filename)[0]
                print(f"Feature vector - plain text - {finger_code_features[:10]}....")
                insert_features_into_database(db_name, label, finger_code_features, circuit)
                print(f"Processed {filename} - Features inserted into the database.")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

def deserialize_encrypted_features(encrypted_blob, circuit):
    """Deserialize the encrypted features using the same circuit."""
    encrypted_value = circuit.deserialize(encrypted_blob)
    return encrypted_value


def view_encrypted_data(db_name="data/fingerprints.db", circuit=None):
    """
    Retrieve and display encrypted features from the database.
    Optionally deserialize the encrypted data if a circuit is provided.
    """
    if circuit is None:
        print("Warning: No circuit provided. Encrypted data will not be deserialized.")
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT label, features FROM fingerprints")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        label = row[0]
        encrypted_blob = row[1]
        print(f"Label: {label}")
        print(f"Encrypted Features (BLOB): {encrypted_blob[:100]}...")  # Print part of the BLOB
        print(f"Length of Encrypted Features: {len(encrypted_blob)}")

        # Deserialize the encrypted features if the circuit is provided
        if circuit:
            try:
                encrypted_value = deserialize_encrypted_features(encrypted_blob, circuit)
                print(f"Deserialized Encrypted Value: {encrypted_value[:10]}")
                decrypted_features = circuit.decrypt(encrypted_value)
                print(f"Decrypted Features: {decrypted_features[:10]}...")
            except Exception as e:
                print(f"Error deserializing encrypted data for {label}: {e}")

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