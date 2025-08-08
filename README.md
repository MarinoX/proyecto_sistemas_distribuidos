# PROYECTO FINAL - MINI PLATAFORMA DE VIDEO STREAMING P2P

UEA: Sistemas distribuidos

Alumno : Jose Abraham Marin Sanchez

Matricula : 2233030514

------------------------------------------------------

*CONTENIDO DEL PROYECTO*

Este proyecto contiene:

* Codigo del sietema distribuido.

* Documentacion de la arquitectura , codigo y funcionamiento.

* Link del video presentacion del proyecto


------------------------------------------------------

*Como probar este proyecto*

1.- Clonar el repositorio.

2.- Tener instalado Docker.


3.- La carpeta del proyecto ya cuenta con un video prueba y los fragmentos dividios en sus carpetas ,pero si se quiere hacer prueba con otro video necesitaras:

Agregar el video a la carpeta utilidades, modificar el nombre del video dentro de dividir.py y ejecutar el dividir.py en terminal estando en la carpata utilidades.

~~~~~
python dividir.py
~~~~~

Finalmento deberas repartir los fragmentos a la carpeta fragmentos_6001 o fragmentos_6002.

4.- En la terminal del IDE estando en la carpeta raiz del proyecto deberas ejecutar el siguiente comando para contruir y levantar el contenedor

~~~~~
docker-compose up --build
~~~~~
     

5.- Para un uso mas sencillo del sistema se recomienda probarlo en swagger para probarlo de manera mas visual, aunque tambien se puede mediante comandos CURL:

Las direcciones a las cuales acceder son:

a) BROKER

~~~~~
http://localhost:5000/apidocs
~~~~~

b) NODO1 

~~~~~
http://localhost:6001/apidocs
~~~~~

c) NODO2

~~~~~
http://localhost:6002/apidocs
~~~~~