https://github.com/ettomarett/hamlaoui-devops

# WaterWatch Project

This repository contains the **WaterWatch Project**, a satellite-driven platform for **assessing water quality** and **detecting algal blooms** using AI models and Sentinel Hub satellite imagery.

It features:

- A **Jakarta EE** backend for user authentication and data processing  
- A **Next.js (TypeScript)** frontend with interactive mapping and multi-tab results display  
- PostgreSQL integration  
- Automated pipelines for data retrieval and multi-model environmental analysis  

---

## Project Overview

### Purpose

This platform enables users to:

- **Select an area of interest (AOI)** via an interactive map  
- **Fetch satellite imagery** from the **Sentinel Hub API**  
- **Analyze water quality** and detect **algal blooms** using multiple AI techniques  
- View results in a clean, tabbed interface  
- Access personalized dashboards with secure authentication  

---

## How It Works

### 1. AOI Selection

Users choose an area on a simple interactive map. The platform records the coordinates and passes them to a processing pipeline.

### 2. Data Retrieval

Once an AOI is confirmed, the system transitions to a results page and:

- Calls the **Sentinel Hub API** to fetch satellite data (e.g., True Color imagery, NDWI index)  
- The satellite data is then passed to various scripts for analysis

### 3. Analysis Pipeline

The retrieved data is processed by **three separate modules**, each corresponding to a tab in the UI:

- **NDWI-based Detection**  
  - Enhances water visibility using the Normalized Difference Water Index  
  - Detects irregularities indicative of algal bloom zones

- **Sen2Coral Analysis**  
  - Uses the **Sen2Coral model** to assess shallow water quality  
  - Offers a coral-focused environmental quality layer

- **Cyanonet Detection (ML-Based)**  
  - A machine learning model trained on algal bloom patterns  
  - Provides a predictive layer using deep learning on spectral bands  

Each script runs independently, and results are visualized in their dedicated tab.

---

## Backend (Jakarta EE)

- RESTful API with JWT-based authentication  
- PostgreSQL for user data  
- Integration with the **Sentinel Hub API**  
- Model pipelines for NDWI, Sen2Coral, and Cyanonet  
- Outputs stored or streamed to the frontend via endpoints  

See [`backend/README.md`](backend/README.md) for deeper backend implementation.
c
---

## Frontend (Next.js)

- Developed with **Next.js (TypeScript)**  
- AOI selection via embedded interactive map  
- Multi-tab results view:
  - **NDWI Tab**: Color-enhanced detection  
  - **Sen2Coral Tab**: Coral health and water quality  
  - **Cyanonet Tab**: Deep learning-based bloom detection  
- Authentication and user dashboard  

See [`frontend/README.md`](frontend/README.md) for more information.

---

## Getting Started

### Prerequisites

- Java 17+  
- Node.js 18+  
- PostgreSQL  
- Maven  
- WildFly 26+

---

### Backend Setup

```bash
cd backend
mvn clean install
```

Deploy the resulting `.war` file to your WildFly server. Ensure PostgreSQL datasource is configured.

Start WildFly:

```bash
./bin/standalone.sh
```

---

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit the app at: [http://localhost:3000](http://localhost:3000)

---

## Integration

See [`INTEGRATION.md`](INTEGRATION.md) for details on:

- AOI coordinate flow  
- Sentinel Hub API request logic  
- NDWI and Sen2Coral data pipelines  
- Cyanonet ML model integration  
- Tabbed rendering and result synchronization  

---

## Access Points

- **Frontend UI**: [http://localhost:3000](http://localhost:3000)  
- **Backend API**: [http://localhost:28080/auth-backend](http://localhost:28080/auth-backend)  
- **WildFly Admin Console**: [http://localhost:29990](http://localhost:29990)  
