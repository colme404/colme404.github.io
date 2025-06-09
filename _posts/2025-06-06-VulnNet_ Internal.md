---
layout: post
title: "VulnNet: Internal"
date: 2025-06-06
categories: [tryhackme, linux, easy]
tags: [vulnnet, ssh, nfs, redis, rsync, smb, TeamCity]
---

* * *
* * *

![20250528152540.png](/assets/media/20250528152540.png)


**VulnNet: Internal** es una máquina de dificultad *fácil* de la plataforma ***tryhackme***. En esta máquina tocaremos varios conceptos variados al estar interactuando con varios servicios distintos hasta poder acceder al objetivo. Una vez dentro, la escalada de privilegios será algo diferente respecto a otras máquinas aprovechándonos de un software que viene instalado en la víctima.


# Reconocimiento

Empezamos haciendo lo de siempre, enviando una traza **ICMP** a la máquina víctima para comprobar la conectividad.

![20250528152754.png](/assets/media/20250528152754.png)

Vemos que la máquina nos responde y que su **TTL** es de *63*, por lo tanto, podemos intuir que estamos ante un **Linux**.

- ***TTL 64 -> Linux***
- ***TTL 128 -> Windows***

En este caso vemos un valor menos en el TTL porque en TryHackMe la petición pasa por un nodo intermediario tanto en entrada como en salida como podemos ver aquí realizando un *traceroute*.

![20250528152840.png](/assets/media/20250528152840.png)


## Escaneo de puertos

Realizaremos un escaneo de puertos con `nmap` para ver qué puertos están *abiertos* y qué *servicios* corren por cada uno de esos puertos.

```bash
nmap -p- -sS --min-rate 5000 -n -vvv -Pn 10.10.16.182 -oG allPorts
```

| Parámetro  | Descripción                                                                                                                                                                                |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| -p-        | Escanea todo el rango de puertos existentes (65535).                                                                                                                                       |
| -sS        | Realiza un escaneo **TCP SYN** (aumenta el sigilo, solo se envían *paquetes SYN*, sin completar el **handshake**).                                                                         |
| --min-rate | Especifica la tasa mínima de paquetes a enviar, en este caso no menos de 5000 paquetes por segundo.                                                                                        |
| -n         | No aplicar resolución DNS.                                                                                                                                                                 |
| -vvv       | Reporta en consola lo que vaya encontrando sin necesidad de esperar a que termine.                                                                                                         |
| -Pn        | No aplica *host discovery*, (útil si el host puede bloquear los pings o los probes ICMP).                                                                                                  |
| -oG        | guarda el output del escaneo en formato *grepeable* para aplicar la función [extractPorts](https://pastebin.com/raw/X6b56TQ8) de S4vitar para así copiarnos los puertos en el portapapeles. |

El resultado es el siguiente.

![20250528153300.png](/assets/media/20250528153300.png)

Vemos que la víctima tiene varios puertos abiertos, vamos a centrarnos en los siguientes:

| **Puerto** | **Servicio** |
| ---------- | ------------ |
| 22         | SSH          |
| 111        | RPC          |
| 139        | NetBIOS      |
| 445        | SMB          |
| 873        | RSYNC        |
| 2049       | NFS          |
| 6379       | REDIS        |

## Enumeración

Vamos a enumerar la versión que corre sobre los servicios que hemos encontrado, aplicándole scripts básicos de enumeración de nmap que forman parte del NSE escritos en *Lua* para comprobar si podemos profundizar algo más.

Primero le pasamos el archivo **allPorts** a la función *extractPorts* (anteriormente referenciado) para copiarnos los puertos en la clipboard.

![20250528153801.png](/assets/media/20250528153801.png)

Aplicamos el escaneo.

```bash
nmap -sC -sV -p22,111,139,445,873,2049,6379,32797,33077,33633,52809 10.10.16.182 -oN targeted
```

| **Parámetro** | **Descripción**                                                |
| ------------- | -------------------------------------------------------------- |
| -sC           | Ejecución de scripts predeterminados de NSE.                   |
| -sV           | Detección de la versión del servicio que corre en cada puerto. |
| -p            | Especificación de puertos                                      |
| -oN           | Guarda el output en formato nmap.                              |

![20250528154051.png](/assets/media/20250528154051.png)

Aquí ya podemos ver cosas como el nombre del host, que es *VULNET-INTERNAL* y que en el **smb** está habilitado el usuario *invitado*. Vamos a empezar por aquí.


# Explotación

Vamos a proceder a la explotación de la máquina, empezando por comprobar qué podemos hacer en el **SMB**.

## SMB

Empezamos probando un script de `nmap` probando todas las vulnerabilidades posibles sobre este protocolo. Nos reporta que es vulnerable un ataque DoS (Denial of Service) por culpa del servicio *regsvc*, pero esto nos es indiferente para ganar acceso.

![20250528155134.png](/assets/media/20250528155134.png)

Ahora con `smbmap` probaremos a enumerar los recursos compartidos del servidor únicamente indicándole el **host**. Con esto accederemos automáticamente con el usuario *guest* y comprobaremos los recursos existentes y que permisos tenemos sobre ellos.

![20250528155850.png](/assets/media/20250528155850.png)

Vemos que tenemos un recurso llamado *shares* con permisos de **lectura**. Vamos a ver su contenido accediendo por medio de una *null session* (sin proporcionar credenciales).

![20250528160414.png](/assets/media/20250528160414.png)

Vemos que tenemos dos directorios, **temp** y **data**, entramos a la primera para ver que hay.

![20250528160856.png](/assets/media/20250528160856.png)

Y vemos el archivo **`services.txt`** que es la primera flag. 

En el directorio **data**, tenemos otros dos archivos, nos lo traemos a nuestra máquina local para ver el contenido.

![20250528161228.png](/assets/media/20250528161228.png)

A priori no vemos información relevante, sigamos adelante. Decido ir a 'tocar' el servicio **NFS**.


## NFS

El **servicio NFS (Network File System)** es un protocolo que permite que sistemas remotos monten sistemas de archivos de manera similar a cómo se montan discos locales. Vamos a empezar enumerando las monturas que NFS que tiene el objetivo de la siguiente manera:

```bash
showmount -e 10.10.16.182
```

![20250528163104.png](/assets/media/20250528163104.png)

Y tenemos una montura de `/opt/conf`. Vamos a montar este recurso en mi equipo local y vemos que tiene varios directorios:

```bash
mount -t nfs 10.10.16.182:/opt/conf ../content
```

![20250528163552.png](/assets/media/20250528163552.png)

Lo que más me llama la atención de aquí es el directorio **redis**, si echamos un vistazo al escaneo realizado por nmap, tenemos el servicio corriendo por el *puerto 6379*. Entramos al directorio y tenemos un archivo de configuración.

![20250528164113.png](/assets/media/20250528164113.png)

Mediante `grep` vamos a buscar todo lo que tenga que ver con **user** y **pass** mediante expresiones regulares y haciendo case insensitive (ignorando mayúsculas y minúsculas).

![20250528164648.png](/assets/media/20250528164648.png)

Y si tenemos buen ojo y leyendo el comentario de encima de lo marcado, veremos que tenemos la **contraseña de autenticación**.


## Redis

**Redis** es una **base de datos muy rápida** que guarda **datos en memoria** (RAM) en lugar de en disco, lo que la hace **ultra rápida**. Con la contraseña encontrada en el archivo de configuración, vamos a conectarnos al servicio:

![20250528171555.png](/assets/media/20250528171555.png)

Ahora vamos a enumerar las ***keys*** que están almacenadas con `keys *`.

![20250528172012.png](/assets/media/20250528172012.png)

Vemos que nos aparece la siguiente flag: `internal flag`, la obtenemos y ahora solo nos quedaría la `user flag` y `root flag`.

![20250528172141.png](/assets/media/20250528172141.png)

Analizando el resto de ficheros, hay uno que me llama especialmente la atención, el `authlist`. Si ponemos `type` delante vemos el tipo de *key* que es, en este caso una lista.

![20250528172420.png](/assets/media/20250528172420.png)

En redis, para leer keys que sean una lista, se usa el comando `lrange`.

```bash
lrange authlist 0 10
```

![20250528172811.png](/assets/media/20250528172811.png)

Vemos que nos muestra cuatro cadenas idénticas codificadas en `base64`, vamos a descodificarlas.

![20250528173127.png](/assets/media/20250528173127.png)

Y nos muestra credenciales de acceso al servicio de `rsync`.


## Rsync

**`Rsync`** es una herramienta de línea de comandos para **copiar y sincronizar archivos o directorios** entre dos ubicaciones, ya sea en la misma máquina o entre máquinas a través de la red. No es un servicio como tal pero puede funcionar de esta manera si así está configurado como es el caso, por el puerto por defecto `873` como nos aparece en nuestro escaneo de **nmap**.

Vamos a enumerar el servicio.

![20250528174738.png](/assets/media/20250528174738.png)

Tenemos un recurso llamado *files*, vamos a acceder a él con las credenciales encontradas para ver con que nos encontramos.

![20250528175112.png](/assets/media/20250528175112.png)

Dentro de *files* tenemos otro recurso llamado *sys-internal* y ahí dentro muchos directorios. Por la confección de los directorios mostrados parece que se está compartiendo todo el árbol del sistema (incluido el `user.txt` que vemos) del usuario **`sys_internal`**. Vemos también el directorio **.ssh**, vamos a ver si contiene alguna clave.

![20250528175615.png](/assets/media/20250528175615.png)

Vemos que no hay ninguna clave almacenada. En este punto, lo que podríamos hacer es generar un par de claves y subir la clave pública (**.pub**) como `authorized_keys`.

![20250528180038.png](/assets/media/20250528180038.png)

Ahora vamos a subir el `id_rsa.pub`.

![20250528180505.png](/assets/media/20250528180505.png)

Accedemos al **SSH**.

![20250528180619.png](/assets/media/20250528180619.png)

Y ya estamos dentro! Vamos a por la flag `user.txt`.

![20250528180728.png](/assets/media/20250528180728.png)


# Escalada de privilegios

Ahora solo nos queda *escalar privilegios* para convertirnos en **root** y acceder a la flag `root.txt`. Investigando un poco el sistema, intentaba probar a abusar binarios con permisos *SUID*, pero no había manera, así que decido moverme por los directorios hasta que encuentro el siguiente en la raíz:

![20250528181053.png](/assets/media/20250528181053.png)

Investigando un poco, veo que es una herramienta de automatización para desarrollo de software. Entro al directorio y abro el *readme.txt*.

![20250528181343.png](/assets/media/20250528181343.png)

Veo que la herramienta ejecuta un *servicio web*, en nuestro caso al ser linux por el **puerto 8111**. 
Vamos a comprobar si el puerto `8111` está ocupado y hay alguna conexión.

![20250528181703.png](/assets/media/20250528181703.png)

Vemos que el cuerpo está ocupado. La única opción que tenemos ahora de acceder al servicio web es mediante **`port-forwarding`**, que lo que se ejecute en el puerto *8111* de la víctima redirigirlo al puerto *8111* de mi máquina local, vamos a ello.

![20250528182244.png](/assets/media/20250528182244.png)

Ahora vamos al navegador y comprobamos si funciona.

![20250528182332.png](/assets/media/20250528182332.png)

Y efectivamente podemos acceder! Nos pone un aviso de que podemos logearnos como **superusuario** para crear una cuenta de **administrador**, adelante entonces.

![20250528182502.png](/assets/media/20250528182502.png)

Nos pide un token de autenticación, vamos a intentar buscarlo dentro del directorio de *TeamCity* con `grep`.

```bash
grep -i -r "authentication token" 2>/dev/null
```

![20250528184902.png](/assets/media/20250528184902.png)

Tenemos estos, vamos probando hasta que funcione uno de ellos.

![20250528185214.png](/assets/media/20250528185214.png)

Entramos a la administración del sitio web. Vamos a crear un nuevo proyecto y luego a darle en *manually*, ponemos el nombre que queramos y lo creamos.

![20250528185416.png](/assets/media/20250528185416.png)

Una vez hecho esto, ahora le damos a *Create build configuration* y ponemos el nombre que queramos aquí también.

![20250528185624.png](/assets/media/20250528185624.png)

Donde pone *root project* le damos, y saldrá el nombre de nuestro proyecto.

![20250528185759.png](/assets/media/20250528185759.png)

![20250528185814.png](/assets/media/20250528185814.png)

A continuación, entramos a nuestro proyecto, luego a la build que habíamos hecho antes, y en la parte izquierda, donde pone *build steps*, entrar para agregar una nueva.

![20250528190117.png](/assets/media/20250528190117.png)

Vemos varias opciones pero me ha llamado la atención la opción de **Command line**, le damos y podemos ver que podemos poner un *script personalizado*. Se me ocurre darle permisos *SUID* a la `/bin/bash` para poder ejecutarla como **root**.

Hacemos click arriba a la derecha donde pone *run* para que cargue el script.

![20250528190426.png](/assets/media/20250528190426.png)

Volvemos a la *shell* y lo comprobamos.

![20250528190609.png](/assets/media/20250528190609.png)

Ya somos **root**!

Vamos a por la flag en el directorio *root*.

![20250528190749.png](/assets/media/20250528190749.png)

Máquina **VulnNet: Internal** completada!
Happy Hacking ;)
