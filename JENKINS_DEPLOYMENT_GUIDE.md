# Jenkins in Minikube - Deployment Guide

## Quick Start (Windows PowerShell)

```powershell
# 1. Navigate to project directory
cd d:\Downloads\AceFit\AceFit

# 2. Run the deployment script
.\deploy-jenkins.ps1
```

## Quick Start (Linux/Mac Bash)

```bash
# 1. Navigate to project directory
cd /path/to/AceFit

# 2. Make script executable
chmod +x deploy-jenkins.sh

# 3. Run the deployment script
./deploy-jenkins.sh
```

## Manual Steps (if script doesn't work)

```powershell
# 1. Configure minikube Docker environment
minikube docker-env | Invoke-Expression

# 2. Build the Docker image
docker build -f CICD/Dockerfile.jenkins -t acefit-jenkins:latest .

# 3. Create namespace and RBAC
kubectl apply -f k8s/k8s-jenkins-rbac.yaml

# 4. Deploy Jenkins
kubectl apply -f k8s/k8s-jenkins-deployment.yaml

# 5. Deploy Jenkins service
kubectl apply -f k8s/k8s-jenkins-service.yaml

# 6. Check deployment status
kubectl get pods -n jenkins
kubectl get svc -n jenkins

# 7. Wait for deployment to be ready
kubectl rollout status deployment/jenkins -n jenkins
```

## Accessing Jenkins

### Option 1: NodePort (Direct)
```powershell
$MINIKUBE_IP = minikube ip
$NODE_PORT = (kubectl get service jenkins -n jenkins -o jsonpath='{.spec.ports[0].nodePort}')
# Open: http://<MINIKUBE_IP>:<NODE_PORT>  (e.g., http://192.168.99.100:30080)
```

### Option 2: Port Forward (Recommended)
```powershell
kubectl port-forward svc/jenkins 8080:8080 -n jenkins
# Open: http://localhost:8080
```

## Get Initial Admin Password

```powershell
kubectl logs deployment/jenkins -n jenkins | Select-String "initialAdminPassword"
# or
kubectl exec -it deployment/jenkins -n jenkins -- cat /var/jenkins_home/secrets/initialAdminPassword
```

## Verify Deployment

```powershell
# Check pods
kubectl get pods -n jenkins

# Check services
kubectl get svc -n jenkins

# Check deployment status
kubectl describe deployment jenkins -n jenkins

# View logs
kubectl logs deployment/jenkins -n jenkins
```

## Stop/Delete Jenkins

```powershell
# Delete everything
kubectl delete namespace jenkins

# Or delete individual components
kubectl delete deployment jenkins -n jenkins
kubectl delete service jenkins -n jenkins
kubectl delete serviceaccount jenkins -n jenkins
kubectl delete clusterrole jenkins
kubectl delete clusterrolebinding jenkins
```

## Troubleshooting

### Pod not starting?
```powershell
# Check pod status
kubectl describe pod <pod-name> -n jenkins

# View logs
kubectl logs <pod-name> -n jenkins

# Check events
kubectl get events -n jenkins
```

### Image not found?
Make sure you've executed `minikube docker-env` to point Docker to minikube's Docker daemon before building the image.

### Port already in use?
Change the nodePort in `k8s-jenkins-service.yaml` to a different port (e.g., 30081, 30082, etc.)

## What This Setup Includes

✓ Jenkins LTS base image
✓ Python3, pip, and Python virtual environment
✓ Git (for cloning repositories)
✓ Sonar Scanner 5.0.1.3006 (for code analysis)
✓ Kubernetes integration with proper RBAC
✓ Persistent data using EmptyDir volume
✓ Resource limits and requests configured
✓ Health checks ready
