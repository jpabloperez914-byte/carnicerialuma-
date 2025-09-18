import hashlib

def hash_password(password):
    """
    Hashea la contraseña proporcionada usando el algoritmo SHA-256.
    Esta es la función centralizada para todo el sistema.
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
