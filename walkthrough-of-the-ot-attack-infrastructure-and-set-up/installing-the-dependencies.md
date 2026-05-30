# Installing the dependencies

**How to install GoLang(Server and client):**\
If from terminal:

sudo apt install golang-go

**Commands to run:**\
Extract here using\
tar -xvzf goland-2021.1.3.tar.gz\
**Make a new folder in usr/local/bin from the package**\
sudo mkdir /usr/local/bin/goland\
**Move the extracted package to usr/local/bin**\
sudo mv goland-2021.1.3/\* /usr/local/bin/goland\
Change directory to cd /usr/local/bin/goland/bin\
Now, We need to give permission to newly created directory using chmod\
sudo chmod +x goland ./goland\
Now we can run Goland ./goland\
We can download the icon for Robo3t from and put it here as we will need to\
make desktop icon later\
For example save it on /bin with name icon.png /usr/local/bin/goland/bin/icon.png

mv icon.png /usr/local/bin/goland/bin\
To make desktop icon for Goland, we can make a file in usr/share/applications\
sudo nano /usr/share/applications/goland.desktop\
&#xNAN;**● How to install NodeJS (server):**\
Commands to run:\
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh\
nvm install --lts\
curl -fsSL https://deb.nodesource.com/setup\_lts.x | sudo -E bash -\
sudo apt install -y nodejs\
&#xNAN;**● How to install Python (server and client):**\
Commands to run:\
Sudo apt install python\
Sudo apt install python3-pip\
&#xNAN;**● How to install Docker(server):**\
Commands to run:\
curl -fsSL https://get.docker.com -o get-docker.sh\
sudo sh get-docker.sh\
Docker –version (to check the version installed)
