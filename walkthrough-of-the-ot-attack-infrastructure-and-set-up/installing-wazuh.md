# Installing Wazuh

**● How to install Wazuh(server):**\
Commands to run:\
sysctl -w vm.max\_map\_count=\
git clone https://github.com/wazuh/wazuh-docker.git -b v4.12.\
cd wazuh-docker/multi-node/\
Optional: Add the following to the generate-indexer-certs.yml file if your system\
uses a proxy. If not, skip this step. Replace\
\<YOUR\_PROXY\_ADDRESS\_OR\_DNS> with your proxy information.

Wazuh App Copyright (C) 2017, Wazuh Inc. (License GPLv2)

services:\
generator:\
image: wazuh/wazuh-certs-generator:0.0.

```
hostname: wazuh-certs-generator
volumes:
```

* ./config/wazuh\_indexer\_ssl\_certs/:/certificates/
* ./config/certs.yml:/config/certs.yml\
  environment:
* HTTP\_PROXY=\<YOUR\_PROXY\_ADDRESS\_OR\_DNS>\
  docker-compose -f generate-indexer-certs.yml run --rm generator\
  docker-compose up -d\
  The stack exposes the following ports:

1514 Wazuh TCP

1515 Wazuh TCP

514 Wazuh UDP

55000 Wazuh server API

9200 Wazuh indexer API

443

### Wazuh dashboard HTTPS

To access your Docker host’s IP address:\
https://\<DOCKER\_HOST\_IP>

This is the default password and username for the wazuh dashboardThis is the default

username and password to access the Wazuh dashboard:

● Username: admin

● Password: SecretPassword

```
To stop the stack:
docker-compose down
```

