
# Curso de creación de aplicaciones web

Este proyecto implementa un sistema de encuestas utilizando [Django](https://www.djangoproject.com/). Se siguen los pasos explicados en el [tutorial de Django](https://docs.djangoproject.com/en/2.1/intro/). Utilizamos este projecto como punto de partida para el [Curso de Creación de Aplicaciones Web](http://swcraftmlg.com/content/curso-de-creación-de-aplicaciones-web).

## Versiones

Las versiones del proyecto han sido pensadas para ser seguidas en orden. Cada nueva versión incorpora una funcionalidad adicional concreta. El número en las versiones sigue la especificación de [Semantic Versioning](http://semver.org/).


### 1.4.0

 - Actualizados los requerimientos del proyecto: hemos actualizado Django de la versión 1.9 a la 2.1.
 - La API de la aplicación `polls` ha sido movida a la aplicación `polls_api`.


### 1.3.0

 - Implementación de una API como subaplicación de `polls` utilizando [Django REST framework](http://www.django-rest-framework.org/).
 - Nuevos requisitos del proyecto incluidos en el archivo `requirements.txt`.
 - Tamaño de página para paginación movido a los `settings` del proyecto.
 - Declarados los atributos `id` de `Question` y `Choice` de forma explícita en el archivo `models.py`.
 - Corregida la ordenación de preguntas cerradas y sin cerrar.
 - Corregido el método `close` del modelo `Question` para salvar los cambios.


### 1.2.0

 - Incorporación de cuotas para evitar abusos en la votación.
 - La hoja de estilo CSS pasa a utilizar rutas relativas para la carga de imágenes.
 - Mejoradas las plantillas HTML.


### 1.1.0

Cambios relativos a la interfaz de usuario de la aplicación:

 - Agregado motor de plantillas [Jinja2](http://jinja.pocoo.org/) e integrado con [Django](https://www.djangoproject.com/).
 - Mejoradas las plantillas HTML utilizando [Bootstrap](http://getbootstrap.com/).


### 1.0.0

Mejoras notables respecto al código del tutorial:

 - Extendido el modelo de datos.
 - Corregido el incremento de votos para evitar problemas por concurrencia.
 - Agregadas fixtures para tener datos de ejemplo.
 - Agregado comando `pollclose` para cerrar una votación.
 - Mejorada la estructuración de las configuraciones del archivo `settings.py`.
 - Creado archivo `requirements.txt` con los requisitos del proyecto.


### 0.x.0

Implementación de las partes del [tutorial de Django](https://docs.djangoproject.com/en/2.1/intro/). Las versiones 0.1.0 a 0.7.0 implementan las partes [1](https://docs.djangoproject.com/en/2.1/intro/tutorial01/), [2](https://docs.djangoproject.com/en/2.1/intro/tutorial02/), [3](https://docs.djangoproject.com/en/2.1/intro/tutorial03/), [4](https://docs.djangoproject.com/en/2.1/intro/tutorial04/), [5](https://docs.djangoproject.com/en/2.1/intro/tutorial07/), [6](https://docs.djangoproject.com/en/2.1/intro/tutorial06/) y [7](https://docs.djangoproject.com/en/2.1/intro/tutorial07/) respectivamente.
