from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter #función para dividir (chunking)
from langchain_google_genai import GoogleGenerativeAIEmbeddings #embedding de Gemini
from langchain_chroma import Chroma #Chroma = vector store
from langchain_core.documents import Document

load_dotenv()

"""
Auditar localmente que no haya chunks vacíos ni duplicados antes de gastar tokens en embeddings
"""
def verificar_integridad(chunks, corpus_original):
    #Recorrer todos los chunks con su indice (i), quitamos espacios/saltos de línea
    #guardo lista de posiciones de cualquier fragmento que haya quedado en blanco
    vacios = [i for i, c in enumerate(chunks) if not c.page_content.strip()]

    #Extraigo el texto plano de cada objeto, lista
    textos = [c.page_content for c in chunks]

    #lista1 = ["manzana","pera", "manzana", "uvas"]
    #set1 = ["manzana","pera", "uvas"]

    #Set/Conjunto es una lista de valores únicos
    #Convierto la lista de textos en un set (para eliminar repetidos automáticamente), y si la longitud es distinta a la original significa que tenemos chunks iguales
    hay_duplicados = len(textos) != len(set(textos))

    if vacios:
        raise ValueError(f"Se detectaron chunks vacíos en los índices: {vacios}")
    if hay_duplicados:
        print("Advertencia: Se detectaron chunks duplicados en el corpus.")

    #Sumar el total de caraceres de todos os chunks generados vs. el total de caracteres del corpus original
    total_chars_chunks = sum(len(c.page_content) for c in chunks)
    total_chars_corpus = sum(len(d) for d in corpus_original)
    print(f"Integridad OK | Chunks: {len(chunks)} | Caracteres (corpus/chunks): {total_chars_corpus}/{total_chars_chunks}")

"""
Recibir un corpus/texto dividirlo, calcular el embedding, y guardar el corpus en mi vector store
"""
def indexar_corpus(corpus, persist_directory, chunk_size=200, chunk_overlap=30, es_documento=False):
    #Dividir en fragmentos más pequeños corpus/texto
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    #División
    #chunks = splitter.create_documents(texts=corpus, metadatas=[{"origen": "manual.pdf", "pagina": 2}]) 
    if not es_documento:
        chunks = splitter.create_documents(corpus) #create_documents: me permite agregar metadatos
    else:
        chunks = splitter.split_documents(corpus)
    
    #verificar_integridad(chunks, corpus)

    #Embedding
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    return vector_store

"""
Función que abre/carga la carpeta existente del disco para leerla. NO GASTO TOKENS
"""
def cargar_vectorstore(persist_directory):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)

def eliminar_por_ids(vectorstore, ids_a_borrar):
    vectorstore.delete(ids=ids_a_borrar)

def agregar_documentos(vectorstore, nuevos_textos, prefijo_id, chunk_size=200, chunk_overlap=30):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    nuevos_chunks = splitter.create_documents(nuevos_textos)

    #Crear los ids
    ids_nuevos = [f"{prefijo_id}_{i}" for i in range(len(nuevos_chunks))] #["doc_0","doc_1","doc_2"]

    #ids_nuevos = []
    #for i in range(len(nuevos_chunks)):
    #   ids_nuevos.append(f"{prefijo_id}_{id}")

    verificar_integridad(nuevos_chunks, nuevos_textos)

    try:
        vectorstore.add_documents(ids=ids_nuevos, documents=nuevos_chunks)
        print(f"Agregados {len(nuevos_chunks)} chunks con el prefijo {prefijo_id}")
    except Exception as error:
        print("Error al agregar nuevos documentos: ", error)

"""
Realiza la búsqueda semántica (por significado, NO POR PALABRA EXACTA) en el vector store.
Devuelve una lista con los resultados semejantes
"""
def buscar_similares(vectorstore, pregunta, k=3):
    #El modelo (Gemini) se encarga únicamente de hacer la traducción de la pregunta a vectores numéricos (gasta tokens)
    #Chroma se encarga de regresarme la lista con los chunks más parecidos
    #Chroma mide la distancia Euclidiana (L2). Entre más bajo sea el número, más cercano es el sifnificado
    resultados = vectorstore.similarity_search_with_score( #with_score regresa también la distancia euclidiana
        query=pregunta, #Gastamos tokens en traducir la pregunta a vectores númericos
        k=k #La cantidad de chunks que quiero que regrese
    )

    #resultados = [{page_contect: "CONTENIDO DEL CHUNK", "metadata": {"fuente": "documento.pdf"}}, {},{}]

    ##resultados_optimizados = []
    #iterar para imprimir todos los resultados
    for i, (doc, score) in enumerate(resultados, start=1):
        print(f"[Resultado {i}] Distancia (score): {score:.4f}")
        print(f"Contenido: {doc}")
        if doc.metadata:
            print(f"Metadata: {doc.metadata}")
    #     if (score < .53):
    #         resultados_optimizados.append(resultados[i-1])

    # print("Resultados optimizados: ", resultados_optimizados)
    # return resultados_optimizados #si se quiere utilizar un límite para la distancia euclidiana
    return resultados

def formatear_contexto(chunks_recuperados):
    lineas = []
    citas = {}

   
    for i, doc in enumerate(chunks_recuperados, start=1):
        #Si el chunk no se indexó con metadata["fuente"], devolverá "desconocida"
        fuente = doc.metadata.get("fuente", "desconocida")
        lineas.append(f"[{i}] {doc.page_content}")
        citas[i] = fuente

    contexto = "\n\n".join(lineas)
    return contexto, citas

def inspeccionar_chunks(vectorstore):
    datos = vectorstore.get() #datos["ids"], datos["documents"], datos["metadatas"]
    total = len(datos["ids"])
    print(f"-- INVENTARIO DE CHUNKS EN CHROMA (Total: {total}) --")

    #[(28892440-6873-4205-8a0a-cabdd740cb5b, "Se reintenta 3 veces", {"fuente": "manual_de_usaurio.txt"}), ..]
    for i, (chunk_id, texto, meta) in enumerate(zip(datos["ids"], datos["documents"], datos["metadatas"]), start=1):
        print(f"[{i}] ID: {chunk_id}")
        print(f"Fuente/Meta: {meta}")
        resumen = texto.replace("\n", " ")[:100] #Quita los saltos de línea y obten solo los primero 100 carcateres
        print(f"Contenido: {resumen}...")


if __name__ == "__main__":
    CARPETA_DB = "vectorstore_ejemplo"

    # corpus = [
    #     "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente.",
    #     "El costo de cada llamada se calcula a partir de totalTokenCount.",
    #     "Las pruebas unitarias del cliente usan mocks y corren en menos de un segundo,",
    # ]

    # #indexar_corpus(corpus, CARPETA_DB) #Almacenar el texto
    # #indexar_corpus(corpus=corpus, persist_directory=CARPETA_DB, chunk_size=250, chunk_overlap=35) 

    # vs = cargar_vectorstore(CARPETA_DB)
    # print("Chunks indexados: ",vs._collection.count()) #Imprime los chunks indexados

    # datos = vs.get()
    # print("Ids almacenados: ", datos["ids"])
    # print("Chunks almacenados: ", datos["documents"])

    # nueva_politica = ["Los envios nacionales tardan entre 5 y 10 días hábiles"]

    # agregar_documentos(
    #     vectorstore=vs,
    #     nuevos_textos=nueva_politica,
    #     prefijo_id="doc_nuevo",
    #     chunk_size=150,
    #     chunk_overlap=20
    # )

    # datos = vs.get()
    # print("Ids almacenados: ", datos["ids"])
    # print("Chunks almacenados: ", datos["documents"])

    # eliminar_por_ids(
    #     vectorstore=vs,
    #     ids_a_borrar=['f9d84925-9486-4503-a128-e00426504958', '1be9dc81-e641-4533-b176-0e2f1fd4369a', '0092a5c6-04e3-47fb-b6b2-8ce307b3c163']
    # )
    # print("IDs después de borrar:", vs.get()["ids"])

    vs = cargar_vectorstore(CARPETA_DB)
    # pregunta = "¿Qué hace el sistema cuando hay un fallo de red o tiempo de espera?"
    # chunks_recuperados = buscar_similares(vs, pregunta, k=2)

    # #k = Cantidad de chunks que quiero que regrese
    # retrievier = vs.as_retriever(search_kwargs={"k":2}) #Adapta lo que tenía en Chroma para poder utilizarlo en LangChain
    # #Ventaja principal: Cadena o Agente
    # #resultados = retrievier.invoke("¿Cuánto tarda un envío en el mismo país?")
    # resultados = retrievier.invoke("¿Qué hace el sistema cuando hay un fallo de red o tiempo de espera?")
    # for r in resultados:
    #     print(r.page_content)

    #Instalación adicional si queremos leer pdf, docs, etc
    with open("manual_de_usuario.txt", "r", encoding="utf-8") as f:
        contenido = f.read()

    documentos = [Document(page_content=contenido, metadata={"fuente": "manual_de_usuario.txt", "fecha": "2026-11-13"})]

    #indexar_corpus(documentos, CARPETA_DB, es_documento=True)

    # datos = vs.get()
    # print("Ids almacenados: ", datos["ids"])
    # print("Chunks almacenados: ", datos["documents"])

    # retriever = vs.as_retriever(search_kwargs={"k":2})
    # chunks_recuperados = retriever.invoke("¿Cuantos reintentos tengo ante un error?")

    # contexto, citas = formatear_contexto(chunks_recuperados)
    # print("--CONTEXTO FORMATEADO--")
    # print(contexto)
    # print("--DICCIONARIO DE CITAS--")
    # print(citas)

    inspeccionar_chunks(vs)

    #consulta = "Cuáles son los errores de credenciales inválidas?"
    #ids_relevantes = {"b703aca9-cc9f-4d4f-b981-b48e84c50005"}