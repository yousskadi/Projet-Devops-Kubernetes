from sqlalchemy import create_engine, MetaData
import base64

# Récupérer le mot de passe du Secret
password_base64 = "UHJvamVjdERldm9wczIwMjMh"  # Remplacez par la valeur réelle depuis votre Secret
password = base64.b64decode(password_base64).decode("utf-8")
print("This is my password that I am looking for", password)
engine = create_engine(f"postgresql://admin:{password}@db:5432/storedb")
print("This is the engine value that I am looking for", engine)
meta = MetaData()

conn = engine.connect()
