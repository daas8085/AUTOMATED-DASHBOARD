#!/bin/bash

# Automated Dashboard Deployment Script

set -e  # Exit on error

# Configuration
ENVIRONMENT=${1:-development}
REGISTRY=${2:-docker.io/yourusername}
TAG=${3:-latest}
NAMESPACE="dashboard"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    # Check kubectl for production
    if [ "$ENVIRONMENT" = "production" ] && ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed"
    fi
    
    log "Prerequisites check passed."
}

# Build Docker image
build_image() {
    log "Building Docker image..."
    docker build -t $REGISTRY/dashboard:$TAG -f infrastructure/Dockerfile .
    
    if [ $? -eq 0 ]; then
        log "Docker image built successfully."
    else
        error "Failed to build Docker image."
    fi
}

# Push to registry
push_image() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log "Pushing image to registry..."
        docker push $REGISTRY/dashboard:$TAG
        log "Image pushed to registry."
    fi
}

# Deploy locally with Docker Compose
deploy_local() {
    log "Deploying locally with Docker Compose..."
    
    # Stop existing containers
    log "Stopping existing containers..."
    docker-compose -f infrastructure/docker-compose.yml down || true
    
    # Build and start containers
    log "Starting new deployment..."
    docker-compose -f infrastructure/docker-compose.yml up -d --build
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Check services
    log "Checking service status..."
    
    # Check dashboard
    if curl -s http://localhost:8501 > /dev/null; then
        log "Dashboard is running at http://localhost:8501"
    else
        error "Dashboard failed to start"
    fi
    
    # Check Airflow
    if curl -s http://localhost:8080 > /dev/null; then
        log "Airflow is running at http://localhost:8080"
    else
        log "Airflow might still be starting..."
    fi
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log "Deploying to Kubernetes..."
    
    # Create namespace if it doesn't exist
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    # Create secrets
    log "Creating/updating secrets..."
    kubectl create secret generic dashboard-secrets \
        --namespace=$NAMESPACE \
        --from-literal=database-url=$DATABASE_URL \
        --from-literal=redis-url=$REDIS_URL \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply configurations
    log "Applying Kubernetes configurations..."
    kubectl apply -f infrastructure/k8s/ -n $NAMESPACE
    
    # Wait for deployment
    log "Waiting for deployment to be ready..."
    kubectl wait --namespace=$NAMESPACE \
        --for=condition=ready pod \
        --selector=app=dashboard \
        --timeout=300s
    
    # Get service URL
    log "Getting service URL..."
    if [ "$CLOUD_PROVIDER" = "minikube" ]; then
        SERVICE_URL=$(minikube service dashboard-service --url -n $NAMESPACE)
    else
        SERVICE_URL=$(kubectl get svc dashboard-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
        if [ -z "$SERVICE_URL" ]; then
            SERVICE_URL=$(kubectl get svc dashboard-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
        fi
    fi
    