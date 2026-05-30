# Installing Caldera

**● How to install Caldera(server):**\
Commands to run:\
git clone https://github.com/mitre/caldera.git --recursive\
cd caldera\
docker build --build-arg VARIANT=full -t caldera.\
docker run -it -p 8888:8888 caldera\
docker run -p 8888:8888 ghcr.io/mitre/caldera:latest<br>
