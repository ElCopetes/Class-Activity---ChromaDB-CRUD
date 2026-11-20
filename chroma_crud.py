import chromadb
import json
from sentence_transformers import SentenceTransformer
 
 
# --------------------------------------------------
# Configuración
# --------------------------------------------------
 
NOMBRE_COLECCION = "the_oswaldos_collection"
 
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

    # Insertar los documentos, IDs y metadatos
    # utilizando el método add().
    embeddings = modelo.encode(documentos).tolist()

    coleccion.add(
        ids=ids,
        documents=documentos,
        metadatas=metadatos,
        embeddings=embeddings
    )
    

    print("\n¡Documentos insertados correctamente!")


# --------------------------------------------------
# Búsqueda semántica
# --------------------------------------------------

def buscar_documentos():

    consulta = input("\nIngresa tu consulta: ")

    # Utilizar query() para recuperar los 4 documentos
    # más similares a la consulta.
    res = coleccion.query(
    query_embeddings=modelo.encode([consulta]).tolist(), n_results=4 )

    # Mostrar los documentos y sus metadatos.
    print(f"\nTop 4 resultados para: '{consulta}'\n")
    for i in range(len(res["ids"][0])):
        print(f"{i+1}. [{res['ids'][0][i]}] distancia: {res['distances'][0][i]:.4f}")
        print(f"   {res['documents'][0][i]}")
        print(f"   Metadatos: {res['metadatas'][0][i]}\n")

# --------------------------------------------------
# Actualizar un documento
# --------------------------------------------------

def actualizar_documento():

    id_documento = input("\nIngresa el ID del documento que deseas actualizar: ")

    # Veo que exista el documento antes de actualizarlo
    anterior = coleccion.get(ids=[id_documento])

    # Si la lista de ids viene vacía, el documento no existe
    if not anterior["ids"]:
        print(f"\nNo existe ningún documento con el ID '{id_documento}'.")
        return

    print("\nTexto anterior:", anterior["documents"][0])
    print("Metadatos:", anterior["metadatas"][0])

    nuevo_documento = input("\nIngresa el nuevo contenido: ")

    # Preguntar si también se quiere cambiar un metadato
    campo = input("\nCampo del metadato a cambiar (Enter para no cambiar): ").strip()

    # Copiar los metadatos actuales del documento
    nuevos_metadatos = dict(anterior["metadatas"][0])

    if campo:
        valor = input(f"Nuevo valor para '{campo}': ").strip()
        nuevos_metadatos[campo] = valor

    # Convertir el nuevo texto en vector con el mismo modelo de la colección
    embeddings = modelo.encode([nuevo_documento]).tolist()

    # Actualizar contenido, vector y metadatos del documento.
    coleccion.update(
        ids=[id_documento],
        documents=[nuevo_documento],
        embeddings=embeddings,
        metadatas=[nuevos_metadatos]
    )

    # Muestro el cambio realizado, para comprobar que se actualizó correctamente
    registro = coleccion.get(ids=[id_documento])
    print("\nNuevo texto:", registro["documents"][0])
    print("Nuevos Metadatos:", registro["metadatas"][0])

    print("\n¡Documento actualizado!")


# --------------------------------------------------
# Eliminar documentos por condición
# --------------------------------------------------

def eliminar_subset():

    campo = input("\nIngresa el campo del metadato: ").strip()
    valor = input("Ingresa el valor que deseas buscar: ").strip()

    # Crear el filtro where con el campo y valor indicados
    filtro = {campo: valor}

    # Consultar los documentos que cumplen la condición ANTES de eliminar
    coincidencias = coleccion.get(where=filtro)
    total = len(coincidencias["ids"])

    if total == 0:
        print(f"\nNo hay documentos con {campo} = '{valor}'.")
        return

    print(f"\nSe encontraron {total} documentos con {campo} = '{valor}':")
    for id_doc, doc in zip(coincidencias["ids"], coincidencias["documents"]):
        print(f"  {id_doc}: {doc[:60]}...")

    # Eliminar los documentos que cumplen la condición
    coleccion.delete(where=filtro)

    # Comprobar que ya no quedan documentos con esa condición
    restantes = coleccion.get(where=filtro)
    if not restantes["ids"]:
        print(f"\nSe eliminaron {total} documentos. Quedan {coleccion.count()} en la colección.")
        print("\n¡Documentos eliminados correctamente!")
    else:
        print("\nError: algunos documentos no se eliminaron.")


# --------------------------------------------------
# Eliminar todos los documentos
# --------------------------------------------------

def eliminar_todos():

    confirmacion = input(
        "\n¿Estás seguro de que deseas eliminar TODOS los documentos? (si/no): "
    )

    if confirmacion.lower() == "si":

        # Checo que haya documentos antes de intentar eliminar
        total = coleccion.count()
        
        if total == 0:
            print("\nNo hay documentos para eliminar.")
            return

        #Si hay documentos, los obtengo para eliminar
        todos = coleccion.get()
        
        # Eliminar todos los documentos utilizando delete().
        if todos["ids"]:
            coleccion.delete(ids=todos["ids"])

        # Comprobar que la colección esté vacía.
        if coleccion.count() == 0:
            print("Se eliminaron", total, "documentos. Restantes:", coleccion.count())
            print("\n¡Todos los documentos fueron eliminados!")
        #En caso de error
        else:
            print("\nError: No se pudieron eliminar todos los documentos.")

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
