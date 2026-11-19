import chromadb
import json
from sentence_transformers import SentenceTransformer
 
 
# --------------------------------------------------
# Configuración
# --------------------------------------------------
 
NOMBRE_COLECCION = "the_oswaldos"
 
# Modelo de embeddings multilingüe; los vectores se generan manualmente
modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
 
cliente = chromadb.PersistentClient(path="./chroma_data")
 
coleccion = cliente.get_or_create_collection(
    name=NOMBRE_COLECCION,
    metadata={"hnsw:space": "cosine"}
)
 
 


# --------------------------------------------------
# Cargar documentos desde JSON
# --------------------------------------------------

def cargar_documentos(ruta):

    with open(ruta, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    documentos = [item["document"] for item in datos]
    metadatos = [item["metadata"] for item in datos]

    return documentos, metadatos


# --------------------------------------------------
# Insertar documentos en ChromaDB
# --------------------------------------------------

def insertar_documentos(documentos, metadatos):

    # Generar un ID para cada documento
    ids = [f"doc_{i}" for i in range(len(documentos))]

    # TODO: Insertar los documentos, IDs y metadatos
    # utilizando el método add().
    col.add (ids = ids
    documents = documentos
    metadata = metadatos
    )
    

    print("\n¡Documentos insertados correctamente!")


# --------------------------------------------------
# Búsqueda semántica
# --------------------------------------------------

def buscar_documentos():

    consulta = input("\nIngresa tu consulta: ")

    # TODO: Utilizar query() para recuperar los 4 documentos
    # más similares a la consulta.
    res = col.query(
        query_texts = [consulta],
        n_results = 4
    )

    # TODO: Mostrar los documentos y sus metadatos.
    print(res)

# --------------------------------------------------
# Actualizar un documento
# --------------------------------------------------

def buscar_documentos():

    consulta = input("\nIngresa tu consulta: ")

    vector = modelo.encode([consulta]).tolist()

    res = col.query(
        query_embeddings=vector,
        n_results=4
    )

    for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
        print("\n", doc)
        print(meta)


# --------------------------------------------------
# Eliminar documentos por condición
# --------------------------------------------------

def eliminar_subset():

    campo = input("\nIngresa el campo del metadato: ")
    valor = input("Ingresa el valor que deseas buscar: ")

    # TODO: Crear un filtro where utilizando el campo y el valor.
    # Ejemplo: {"category": "programming"}

    # TODO: Eliminar los documentos que cumplan la condición
    # utilizando delete().

    # TODO: Comprobar que los documentos fueron eliminados
    # utilizando get().

    print("\n¡Documentos eliminados correctamente!")


# --------------------------------------------------
# Eliminar todos los documentos
# --------------------------------------------------

def eliminar_todos():

    confirmacion = input(
        "\n¿Estás seguro de que deseas eliminar TODOS los documentos? (si/no): "
    )

    if confirmacion.lower() == "si":

        # TODO: Obtener los IDs de todos los documentos utilizando get().

        # TODO: Eliminar todos los documentos utilizando delete().

        # TODO: Comprobar que la colección esté vacía.

        print("\n¡Todos los documentos fueron eliminados!")

    else:
        print("\nOperación cancelada.")


# --------------------------------------------------
# Menú principal
# --------------------------------------------------

def main():

    # Cargar documentos solamente si la colección está vacía
    if coleccion.count() == 0:

        documentos, metadatos = cargar_documentos("documents.json")

        insertar_documentos(documentos, metadatos)

    while True:

        print("\n========== MENÚ CHROMADB ==========")
        print("1. Buscar documentos")
        print("2. Actualizar un documento")
        print("3. Eliminar documentos por condición")
        print("4. Eliminar todos los documentos")
        print("5. Salir")

        opcion = input("\nSelecciona una opción: ")

        if opcion == "1":
            buscar_documentos()

        elif opcion == "2":
            actualizar_documento()

        elif opcion == "3":
            eliminar_subset()

        elif opcion == "4":
            eliminar_todos()

        elif opcion == "5":
            print("\n¡Hasta luego!")
            break

        else:
            print("\nOpción no válida. Intenta nuevamente.")


if __name__ == "__main__":
    main()
