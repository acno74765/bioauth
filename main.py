# main.py

import os
import numpy as np
from src.database import create_and_populate_database, view_encrypted_data
from src.secure_computation import generate_paillier_keypair, secure_distance_computation, decrypt_and_unmask_distances

if __name__ == "__main__":
    # Directory containing fingerprint images
    fingerprint_dir = "data/fingerprints"
    
    # Create and populate the database from the fingerprint images
    create_and_populate_database(fingerprint_dir)
    view_encrypted_data()
    # Generate a public-private key pair for Paillier encryption
    #public_key, private_key = generate_paillier_keypair()
    
    # Example client's 640-dimensional feature vector
    #client_vector = np.random.randint(0, 256, 640)

    # Load the database from the SQLite file 
    #from src.database import get_features_from_database
    #database = [get_features_from_database("data/fingerprints.db", label) for label in ["fingerprint_001", "fingerprint_002"]]

    # Perform secure distance computation
    #masked_encrypted_distances = secure_distance_computation(client_vector, database, public_key)

    # Client decrypts and unmasks the distances
    #decrypted_distances = decrypt_and_unmask_distances(masked_encrypted_distances, private_key)

    # Print the decrypted distances
    #print("Decrypted Squared Distances:", decrypted_distances)

    # label_to_delete = "fingerprint"  # Change this to the label you want to delete
    # delete_entry(label_to_delete)




































# import os
# from src.database import create_and_populate_database, get_features_from_database
# from src.secure_computation import generate_paillier_keypair

# if __name__ == "__main__":
  
#     fingerprint_dir = "data/fingerprints"
    
#     # create_and_populate_database(fingerprint_dir)

   
#     # public_key, private_key = generate_paillier_keypair()
    
#     # print("Database populated and key pair generated.")

# features = get_features_from_database("data/fingerprints.db", "fingerprint")
# if features is not None:
#     print("Retrieved features:", features)



    