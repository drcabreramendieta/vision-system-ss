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
