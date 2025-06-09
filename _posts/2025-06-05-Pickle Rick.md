---
layout: post
title: "PickleRick"
date: 2025-06-05
categories: [tryhackme, linux, easy]
tags: [picklerick, webshell, bypass]
---

* * *
* * *

![20250605120056.png](/assets/media/20250605120056.png)


**Pickle Rick** es una máquina *linux* de dificultad fácil de la plataforma de ***tryhackme***. En esta máquina tendremos que encontrar tres "ingredientes" para ayudar a Rick, que equivalen a tres **flags**. Encontraremos un panel de comandos con restricciones de alguno de ellos, vamos a ello.


# Reconocimiento

Enviaremos una traza **ICMP** a la máquina víctima para comprobar la conectividad.

![20250605120623.png](/assets/media/20250605120623.png)

Vemos que la máquina nos responde y que su **TTL** es de *63*, por lo tanto, podemos intuir que estamos ante un **Linux**.

- ***TTL 64 -> Linux***
- ***TTL 128 -> Windows***

En este caso vemos un valor menos en el TTL porque en TryHackMe la petición pasa por un nodo intermediario tanto en entrada como en salida como podemos ver aquí realizando un *traceroute*.

![20250605120650.png](/assets/media/20250605120650.png)

## Escaneo de puertos

Realizaremos un escaneo de puertos con `nmap` para ver qué puertos están *abiertos* y qué *servicios* corren por cada uno de esos puertos.

```bash
nmap -p- -sS --min-rate 5000 -n -vvv -Pn 10.10.220.136 -oG allPorts
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

Nos reporta lo siguiente.

![20250605120836.png](/assets/media/20250605120836.png)

| **Puerto** | **Servicio** |
| ---------- | ------------ |
| 22         | SSH          |
| 80         | HTTP         |

## Enumeración

Vamos a enumerar la versión que corre sobre los servicios que hemos encontrado, aplicándole scripts básicos de enumeración de nmap que forman parte del NSE escritos en *Lua* para comprobar si podemos profundizar algo más.

Primero le pasamos el archivo **allPorts** a la función *extractPorts* (anteriormente referenciado) para copiarnos los puertos en la clipboard, en este caso no es necesario pero en casos donde tengamos muchos puertos agiliza el trabajo.

![20250605120927.png](/assets/media/20250605120927.png)

Aplicamos el escaneo.

```bash
nmap -sC -sV -p22,80 10.10.220.136 -oN targeted
```

| **Parámetro** | **Descripción**                                                |
| ------------- | -------------------------------------------------------------- |
| -sC           | Ejecución de scripts predeterminados de NSE.                   |
| -sV           | Detección de la versión del servicio que corre en cada puerto. |
| -p            | Especificación de puertos                                      |
| -oN           | Guarda el output en formato nmap.                              |

![20250605121048.png](/assets/media/20250605121048.png)

Vemos que tenemos la versión del *SSH* actualizada y que el servidor web es un apache dentro de un *ubuntu*.

## Servicio HTTP (Puerto 80)

Vamos a empezar entrando al servicio web y ver que podemos encontrar.

![20250605121348.png](/assets/media/20250605121348.png)

Vemos que es una web sencilla, sin ningún botón o modo para interactuar con ella, vamos a ver que tenemos en el código fuente.

![20250605121507.png](/assets/media/20250605121507.png)

Llama la atención ese comentario recordando el usuario, `R1ckRul3s`, aquí tenemos un potencial usuario, lo anotamos porque puede ser importante.

Procedemos a realizar *fuzzing* en búsqueda de directorios y archivos en el servidor web, de la siguiente manera.

```bash
gobuster dir -u http://10.10.220.136 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x txt,py,php,sh,css,pdf,js,html
```

![20250605122130.png](/assets/media/20250605122130.png)

Parece que nos ha encontrado dos directorios interesantes, **login.php** y **portal.php** que hace redirección a la primera al no estar autenticado. También tenemos un **robots.txt**, vamos a ver qué contiene.

![20250605122205.png](/assets/media/20250605122205.png)

Vemos una palabra extraña, lo que interpreto que podría ser una contraseña, que junto al usuario que hemos encontrado antes, podríamos probar a autenticarnos en el panel de login.

![20250605122357.png](/assets/media/20250605122357.png)

![20250605122425.png](/assets/media/20250605122425.png)

Las credenciales son válidas y entramos en un panel de comandos, si intentamos entrar en alguna de las secciones de arriba, nos saldrá lo siguiente.

![20250605122531.png](/assets/media/20250605122531.png)


# Primera flag

Aún no tenemos permisos suficientes. Si volvemos al panel de comandos y hacemos un *ls* nos mostrará un `.txt` que parece contener uno de los tres ingredientes.

![20250605122738.png](/assets/media/20250605122738.png)

Vamos a ver el contenido de este archivo.

![20250605122822.png](/assets/media/20250605122822.png)

Pero al hacer un `cat` nos dice que ese comando está deshabilitado. Bien, viendo que hay filtros de algunos comandos, vamos a probar el `tac`, que es similar pero a la inversa, imprime la salida de un archivo empezando desde la línea inferior hasta la línea superior.

![20250605123310.png](/assets/media/20250605123310.png)

Y esta vez nos funciona! Tenemos el primer ingrediente.

Mencionar que **cat** no es el único comando deshabilitado, si probamos a hacer un `tac` al *portal.php* veremos que *head, more, tail, vim, vi y nano* también lo están

![20250605123705.png](/assets/media/20250605123705.png)

# Segunda flag

Si hacemos otra vez un *ls*, veíamos otro txt, llamado `clue.txt`, vamos a ver el contenido.

![20250605123847.png](/assets/media/20250605123847.png)

Nos da una pista de donde puede estar, vamos a mirar por el directorio `/home` con `ls -la /home`.

![20250605124108.png](/assets/media/20250605124108.png)

Tenemos un directorio de usuario llamado `rick`, vamos a listar el contenido con `ls -la /home/rick`.

![20250605124238.png](/assets/media/20250605124238.png)

Ahí lo tenemos, vamos a abrirlo entrecomillado al tener un espacio, o con una contrabarra después del *second*, cualquiera de las dos opciones es válida, sino el comando no funcionará.

- tac “/home/rick/second ingredients”)
- tac /home/rick/second\ ingredients

![20250605124617.png](/assets/media/20250605124617.png)

Segundo ingrediente conseguido, vamos a por el tercer y último ingrediente.

# Tercera flag

Para obtener la última flag, intuyo que estará en el directorio **root**, pero si hacemos un `whoami`, vemos que somos **www-data** y si probamos a acceder al directorio **root** no tenemos permisos.

![20250605125320.png](/assets/media/20250605125320.png)

Si hacemos un `sudo -l` podemos probar a ver si nuestro usuario puede ejecutar algún comando con privilegio de *superusuario*. 

![20250605125545.png](/assets/media/20250605125545.png)

Al hacerlo, nos sale un *output* diciéndonos que el usuario **www-data**, que es el que somos ahora, puede ejecutar cualquier comando `sudo` sin necesidad de contraseña.
Vamos a probarlo listando los archivos del directorio *root* con **sudo** delante de la siguiente manera:

```bash
sudo ls -la /root
```

![20250605125829.png](/assets/media/20250605125829.png)

Ahí tenemos la tercera flag, `3rd.txt`. Vamos a abrirla con `sudo tac /root/3rd.txt`.

![20250605130019.png](/assets/media/20250605130019.png)

Y ahí tenemos el tercer y último ingrediente para Rick, hemos completado la máquina!

# Método alternativo (reverse shell)

Durante la máquina nos hemos pasado gran parte del tiempo en el panel de comandos, pero podríamos habernos entablado una reverse shell de la siguiente manera poniéndonos a la escucha con *netcat*.


![20250605130449.png](/assets/media/20250605130449.png)

![20250605130512.png](/assets/media/20250605130512.png)

De esta manera, estaríamos dentro de la máquina directamente y podríamos utilizar todos los comandos deshabilitados anteriormente como `cat`.

Al poder ejecutar cualquier comando con `sudo` delante sin necesidad de contraseña, haciendo un simple `sudo su` ya nos convertiríamos automáticamente en **root**.

![20250605130953.png](/assets/media/20250605130953.png)

Hasta aquí la máquina **Pickle Rick**
Happy Hacking ;)
