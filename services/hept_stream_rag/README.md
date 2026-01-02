# Hept Stream RAG
## Component ID: SYS-HSR-8.1

The **Hept Stream RAG** (Retrieval-Augmented Generation) system manages the seven semantic streams of EVA's long-term memory.

### 📁 Directory Structure

- **`configs/`**: Configuration & Master Registries.
  - `Hept_Stream_RAG_Interface.yaml`: Public API specification.
  - `Hept_Stream_RAG_Input_Contract.yaml`: Master Input Registry.
  - `Hept_Stream_RAG_Output_Contract.yaml`: Master Output Registry.

- **`contract/`**: Detailed bilateral agreements.
  - `upstream/`: Sources for memory streams.
  - `downstream/`: Destinations for retrieved context.

### 🔗 Integration Flow

1. **Input**: Receives context anchors from **CIN** and encoded memories from **MSP**.
2. **Process**: Performs vector search across 7 specialized streams (Emotional, Physical, Semantic, etc.).
3. **Output**: Sends retrieved context nodes to **CIN** for prompt enrichment.

### 📊 Key Specifications

- **Latency**: < 200ms
- **State**: Stateless (Interface to Vector DB)
- **Version**: 8.1.0
