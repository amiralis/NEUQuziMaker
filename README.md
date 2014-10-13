NEU Quzi Maker
==============

Online Quiz Generator

![demo image](https://raw.githubusercontent.com/amiralis/NEUQuziMaker/master/static/screenshot.png)


## SSL Setup

The app depends on client's SSL certificate for authentication and logging the answers, to generate the clients key and certificate:

```bash
$ openssl genrsa -out $EMAIL $KEY_SIZE
$ openssl req -new -key $EMAIL -subj "/C=US/ST=MA/L=Boston/O=NEU/OU=$SEMESTER/\
CN=$EMAIL/emailAddress=$EMAIL" -out $EMAIL.csr
$ openssl ca -in $EMAIL.csr -cert $CA_crt -keyfile $CA_key -out $EMAIL.crt
$ openssl pkcs12 -export -clcerts -in $EMAIL.crt -inkey $EMAIL.key -out $EMAIL.p12\ 
-passout pass:$PASSWORD
```

To verify and pass the client's certificate fields to the app, add the following to the apache config file:

```bash
SSLVerifyClient require
SSLVerifyDepth 2
SSLOptions +StdEnvVars
```