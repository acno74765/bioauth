import numpy as np
from phe import paillier

#Homomorphic encryption
def generate_paillier_keypair():
    """Generate a public-private key pair for Paillier encryption."""
    public_key, private_key = paillier.generate_paillier_keypair()
    return public_key, private_key

def encrypt_vector(vector, public_key):
    """Encrypt a vector using Paillier encryption."""
    # Convert each element to a Python int before encryption
    encrypted_vector = [public_key.encrypt(int(x)) for x in vector]
    return encrypted_vector

#Euclidean Distance
def compute_encrypted_squared_distance(encrypted_vector, db_vector, public_key):
    """Compute the squared Euclidean distance between the encrypted vector and a database vector."""
    assert len(encrypted_vector) == len(db_vector), "Vectors must be the same length"
    
    encrypted_distance = public_key.encrypt(0)  # Initialize with zero encryption

    for enc_val, db_val in zip(encrypted_vector, db_vector):
        # Convert db_val to a Python float to avoid precision issues with NumPy types
        db_val = float(db_val)

        # Compute the term -2 * v1[i] * v2[i] (encrypted)
        encrypted_term2 = enc_val * (-2 * db_val)  # Paillier supports multiplying an encrypted value by a plaintext

        # Add the encrypted term to the running total
        encrypted_distance += encrypted_term2

        # Add v2[i]^2 (plain text) to the running total
        encrypted_distance += public_key.encrypt(db_val * db_val)

    return encrypted_distance

#Masking and secure distance computation
def mask_encrypted_distances(encrypted_distances, public_key):
    """Mask the encrypted distances with random values."""
    masked_encrypted_distances = []
    for enc_dist in encrypted_distances:
        mask = np.random.randint(1, 100000)
        masked_enc_dist = enc_dist + public_key.encrypt(mask)
        masked_encrypted_distances.append((masked_enc_dist, mask))
    return masked_encrypted_distances

def secure_distance_computation(client_vector, database, public_key):
    """Perform secure distance computation between a client's encrypted vector and a database."""
    # Encrypt the client's feature vector
    encrypted_client_vector = encrypt_vector(client_vector, public_key)
    
    # Compute the encrypted squared distances
    encrypted_distances = []
    for db_vector in database:
        encrypted_distance = compute_encrypted_squared_distance(encrypted_client_vector, db_vector, public_key)
        encrypted_distances.append(encrypted_distance)
    
    # Mask the encrypted distances
    masked_encrypted_distances = mask_encrypted_distances(encrypted_distances, public_key)
    
    return masked_encrypted_distances

def decrypt_and_unmask_distances(masked_encrypted_distances, private_key):
    """Decrypt the masked encrypted distances and remove the masking values."""
    decrypted_distances = []
    for masked_enc_dist, mask in masked_encrypted_distances:
        # Decrypt the masked distance
        decrypted_value = private_key.decrypt(masked_enc_dist)
        # Unmask the distance by subtracting the mask
        unmasked_distance = decrypted_value - mask
        decrypted_distances.append(unmasked_distance)
    return decrypted_distances
