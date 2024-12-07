from concrete import fhe

def add(x, y):
    return x + y

compiler = fhe.Compiler(add, {"x": "encrypted", "y": "encrypted"})
inputset = [(3, 5), (7, 8)]
circuit = compiler.compile(inputset)

circuit.keygen()
enc_x, enc_y = circuit.encrypt(3, 5)
enc_result = circuit.run(enc_x, enc_y)
result = circuit.decrypt(enc_result)

print("Encrypted addition result:", result)
