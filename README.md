Generating SSL key:

    openssl ecparam -name secp521r1 -out secp521r1.pem
    openssl req -newkey ec:secp521r1.pem -outform PEM -out ircd.csr -keyout ircd.key -new -batch -nodes -subj /CN=irc
    openssl x509 -req -days 365 -in ircd.csr -signkey ircd.key -out ircd.crt
    cat ircd.key ircd.crt >> ircd.pem
