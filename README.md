# TUMSA

Backend de la aplicacion de TUMSA.

## Comenzando 🚀

Esta aplicacion fue desarrollada en python2 por lo que para usarla de manera local se debera de clonar el proyecto e instalar Python2. 
Debido a las dependencias con ciertas librerias se recomienda usar Python 2.7.
Tambien se puede construir la version para Docker.


### Pre-requisitos 📋

Esta aplicacion puede funcionar de manera local o en algun servicio de contenedores como ECS, Kubernetes, Docker Swarm. 
Para construir la aplicacion de manera local se debe de contar con la version de Python 2.7 y el instalador paquetes pip.

```
pip install -r requierements.txt
```

Para construir la version de docker se puede hacer:

```
docker build -t tumsa-backend:dev .
```
Debido a una restriccion en las imagenes de AWS ECR ya no permite descargar imagenes de github durante el deployment usando codebuild por lo que se replicaron algunas imagenes en el registry de AWS como se puede ver en el DockerFile

```
FROM 042469170563.dkr.ecr.us-east-1.amazonaws.com/python:2.7
```

## Recomendaciones al hacer cambios ⚙

Todos los cambios deben de ser gestionados en una branch diferente a la master branch, además se debe de controlar la version de la aplicacion usando los archivos app.json y buildspec.yml

_buildspec.yml_
```
env:
  variables:
      AWS_DEFAULT_REGION: "us-east-1"
      AWS_ACCOUNT_ID: "042469170563"
      VERSION: 1.3.4
```
_package.json_
```
{
  "name": "tumsa",
  "version": "1.3.4",
```
Estos numeros de version serán usados al momento del despliegue en AWS.


El codigo funciona como un API y fue desarrollado usando la libreria Flask por lo que :

_views_
```
Contiene el codigo principal para las diferentes vistas o archivos html para ser desplegados al usuario final. Por ejemplo: 404.html cuando no se encuentra una pagina o se ha denegado el acceso
```
_routes_
```
Contiene los archivos de nodejs del lado del servidor, solo hay dos un index.js y el api.js. El primero controla la session del usuario asi como el correcto redireccionamiento de las paginas, y el segundo es un middleware entre el controllador (AngularJS) y el backend de la misma aplicacion
```
_public_
```
Contiene archivos como imagenes, hojas de estilo y archivos de javascript que serán ejecutados del lado del cliente(navegador) 
```

## Construido con 🛠️

_Herramientas usadas para el frontend_

* [AngularJS](https://angularjs.org/)
* [NodeJS](https://nodejs.org/en/)
* [Bootstrap](https://getbootstrap.com/)
