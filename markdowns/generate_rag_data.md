# Tutorial: ChromaDB füllen (Django Management Command)

Dieses Tutorial zeigt, wie dein System Textdateien zerlegt, embeddet und in ChromaDB speichert. Das Ziel ist:
**Deine RAG-Funktionen sollen später kontextbezogene Antworten generieren können.**

---

# 1. Ziel des Commands

Du hast Textdateien (z. B. FAQ, Dokumentation, Wissenstexte).
Diese sollen:

1. **gelesen**
2. **in überlappende Chunks geteilt**
3. **embedded (Vektor-Repräsentationen)**
4. **mit Metadaten versehen**
5. **als ChromaDB-Collection gespeichert**

Danach kannst du mit einem Prompt kontextbezogene Textteile aus Chroma abrufen.

---

# 2. Command ausführen

```
python manage.py generate_rag_day --collection=eventim
```

Dies erzeugt (falls noch nicht vorhanden):

```
/chroma_db/<collection_name>
```

und speichert dort alle Chunks + Embeddings.

---

# 3. Ablaufdiagramm

```mermaid
flowchart TD

A[Textdatei laden] --> B[split_text → Text in Chunks teilen]
B --> C[Metadaten erstellen (source, index, length)]
C --> D[OpenAI EmbeddingWrapper → Embedding erzeugen]
D --> E[Chroma.from_texts(...)]
E --> F[Chunks + Embeddings in Collection speichern]
```

---

# 4. Die Komponenten (einfach erklärt)

## 4.1 `split_text()` — Text in Chunks

Dein Splitter:

* chunk_size ≈ 500 Zeichen
* Overlap ≈ 150 Zeichen
* sorgt dafür, dass der Kontext bei jeder Chunk-Grenze erhalten bleibt

Ergebnis:

```
["Chunk 1...", "Chunk 2...", ...]
```

---

## 4.2 Metadaten generieren

Zu jedem Chunk wird ein Metadaten-Dict erzeugt:

```
{
  "source": "eventim_1.txt",
  "chunk_index": 0,
  "length": 482
}
```

Diese Metadaten erlauben:

* Filtern
* Debugging
* Source-Tracking
* späteres Hervorheben im UI

---

## 4.3 Embeddings erzeugen

Du nutzt einen kleinen Wrapper:

```
OpenAiEmbeddingWrapper → nutzt text-embedding-3-small
```

Er kann:

* `embed_documents([...])`
* `embed_query("...")`

Damit arbeitet ChromaDB und LangChain problemlos zusammen.

---

## 4.4 Speichern in ChromaDB

Ein einzelner Aufruf:

```
Chroma.from_texts(
    texts=[...],
    embedding=embedding_wrapper,
    collection_name="eventim",
    client=PersistentClient(...),
    metadatas=metadatas,
    ids=[filename-index]
)
```

Wichtig:

* `PersistentClient` erzeugt ein echtes lokales Chroma-Verzeichnis
* Jeder Chunk erhält eine **stabile ID** wie `eventim_1.txt-12`
* Mehrfaches Ausführen überschreibt bestehende IDs

---

# 5. Gesamtprozess des Commands

Das Management Command macht:

1. Iteration über deine Dateien (z. B. `eventim_1.txt`)
2. Text laden
3. Chunks erzeugen → `split_text`
4. Metadaten generieren
5. Übergabe an `store_chunks()`
6. ChromaDB legt Collection an oder ergänzt sie

Dadurch entsteht eine **durchsuchbare, embeddings-basierte Wissensdatenbank**.

---

# 6. Nutzung: RAG-Kontext abfragen

Später im Chatbot:

```
result = collection.query(
    query_embeddings=[embed(prompt)],
    n_results=3
)
```

→ Du bekommst die **3 ähnlichsten Chunks** als Kontext für OpenAI.

Serverseitig sieht das so aus:

```
get_context_chunks(collection, prompt)
→ ["Chunk A", "Chunk B", "Chunk C"]
```

Diese Chunks wandern dann in den Systemprompt deines RAG-Bots.
