# MSP Client
## Component ID: SYS-MSP-C-8.1

The **MSP Client** is the specialized adapter for interacting with the Memory & Soul Passport system, ensuring data integrity and serializability.

### 📁 Directory Structure

- **`configs/`**: Configuration & Master Registries.
  - `MSP_Client_Interface.yaml`: Public API specification.
  - `MSP_Client_Output_Contract.yaml`: Master Output Registry.

- **`contract/`**: Detailed bilateral agreements.
  - `downstream/`: Connection to MSP engine.

### 📊 Key Specifications

- **State**: Persistent (Local buffers)
- **Version**: 8.1.0
