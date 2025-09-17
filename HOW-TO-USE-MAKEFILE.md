# How to build & push images to Harbor
## 1) Requirements

- Docker (with Buildx enabled)
- curl

## 2) Edit the make.local based on your credential and image detail

make.local :
```
HARBOR_USER = your-username      
HARBOR_PASSWORD = your-password  
IMAGE = test-rapp        
TAG   = 1.0.0            
```
## 3) Execute

From the repo root:
```
make build-push
```