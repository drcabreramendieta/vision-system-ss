**Estructura General de los Módulos definidos en la arquitectura C4**

La organización de carpetas presentada (adapters, application, domain, ports), contempla lo siguiente:

**domain/**
  Aquí residen las clases de dominio (entidades, objetos de valor, servicios de dominio puros).

**application/**
  Contiene los casos de uso o servicios de aplicación, que orquestan la lógica entre el dominio y los puertos.

**ports/**
  Define interfaces (puertos) tanto de entrada (inbound) como de salida (outbound).

**adapters/**
  Contiene las implementaciones concretas de los puertos, o bien los “controladores”/“controladores externos” que exponen el servicio (REST, gRPC, invocación directa, etc.).

Bajo un enfoque de Arquitectura Hexagonal, el core (domain + application) no sabe nada de infraestructura o módulos externos. Las interfaces que el core ofrece o requiere se definen en la carpeta ports; las implementaciones de dichas interfaces se hallan en adapters.

**Ejecución**
1. Agregar la ruta del archivo mp4 a config.yaml.
2. En un terminal ejecutar:
```
export PYTHONPATH=src/
fastapi run src/application.py --reload
```
3. En el navegador acceder a la url http://localhost:8000/docs

# TODO:
- El adaptador de frames locales debe capturar y emitir los frames en un hilo diferente al principal. Caso contrario la ejecución de la petición no termina.
- Se debe generar el contenedor para todos los módulos siguiendo los lineamientos del de Video.
- Se debe modificar el contenedor de aplicación agregando los otros contenedores y las dependencias.
- Revisar los tipos de datos de retorno de los servicios en cada módulo.