# Lost City Explorer

A collaborative platform that leverages satellite imagery, machine learning, and GIS tools to help discover and explore archaeological sites.

## Project Structure

```
LostCityExplorer/
├── backend/                # Jakarta EE application 
├── frontend/               # React application
├── ml_ai/                  # Python-based machine learning service
├── gis_tools/              # JavaScript/CesiumJS GIS tools
├── docker-compose.yml      # Docker Compose for local development
├── kubernetes/             # Kubernetes deployment manifests
│   ├── backend/            # Backend service and deployment
│   ├── frontend/           # Frontend service and deployment
│   ├── db/                 # Database service and deployment
│   └── ingress/            # Ingress configuration
├── .github/                # GitHub configuration
│   └── workflows/          # CI/CD pipelines
└── README.md               # This file
```

## Team Responsibilities

This project is designed for a team of four people:

1. **Backend Developer**: Responsible for the Jakarta EE API, database integration, and authentication.
2. **Frontend Developer**: Handles the React.js UI, WebGL visualizations, and user interactions.
3. **Machine Learning Specialist**: Develops the AI models for archaeological feature detection.
4. **GIS Specialist**: Creates spatial analysis tools and integrates geospatial functionality.

Each component directory contains a detailed README file with specific setup instructions for the responsible team member.

## Local Development with Docker

Each service can be developed and tested individually using Docker, or the entire system can be run using Docker Compose.

### Prerequisites

- Docker and Docker Compose
- Git

### Getting Started

1. Clone the repository:

```bash
git clone https://github.com/your-org/LostCityExplorer.git
cd LostCityExplorer
```

2. Start all services with Docker Compose:

```bash
docker-compose up -d
```

This will start:
- Jakarta EE backend on port 8080
- React frontend on port 3000
- ML/AI service on port 5000
- GIS tools on port 3001
- PostgreSQL database on port 5432

3. Access the various components:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8080
   - ML/AI Service: http://localhost:5000
   - GIS Tools: http://localhost:3001

### Individual Component Development

Each team member can work on their component independently:

1. **Backend Developer**: See `backend/README.md` for Jakarta EE setup and development instructions.

2. **Frontend Developer**: See `frontend/README.md` for React.js setup and development instructions.

3. **ML/AI Specialist**: See `ml_ai/README.md` for Python ML/AI environment setup and development instructions.

4. **GIS Specialist**: See `gis_tools/README.md` for Node.js and CesiumJS setup and development instructions.

## Kubernetes Deployment

For production deployment, Kubernetes manifests are provided:

1. Create the necessary secrets:

```bash
kubectl create secret generic db-credentials \
  --from-literal=db-name=lostcity \
  --from-literal=db-user=lostcity \
  --from-literal=db-password=secure-password
```

2. Apply the Kubernetes manifests:

```bash
kubectl apply -f kubernetes/db/
kubectl apply -f kubernetes/backend/
kubectl apply -f kubernetes/frontend/
kubectl apply -f kubernetes/ingress/
```

## Docker Image Building

The project includes a GitHub Actions workflow that automatically builds and pushes Docker images to DockerHub when changes are pushed to the main branch.

## Development Workflow

1. Create a feature branch from main
2. Implement changes and test locally with Docker Compose
3. Create a Pull Request to merge into main
4. After review and approval, changes will be automatically deployed

## Contact

For any questions or issues, please contact the project maintainers. 