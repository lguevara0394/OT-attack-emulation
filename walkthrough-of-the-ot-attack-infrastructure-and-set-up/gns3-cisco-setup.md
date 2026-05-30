# GNS3 Cisco Setup

Important thing to notice for ArcaneDoor we will need a router emulation we used GNS3 for it in\
order to best emulate the attack: https://www.gns3.com/\
In order to install the Cisco OS on this router emulator follow the next steps:\
**Prerequisites**\
● GNS3 installed (version 2.x recommended)\
● A legitimate Cisco IOS image (.bin or .image file) — you must obtain this through a\
valid Cisco license/contract or Cisco's DevNet sandbox\
● Sufficient RAM on your host machine\
**Step 1: Open GNS3 and Launch the Setup Wizard**

1. Open **GNS**
2. Go to **Edit → Preferences** (Windows/Linux) or **GNS3 → Preferences** (Mac)
3. Navigate to **Dynamips → IOS Routers**
4. Click **New**\
   **Step 2: Add the IOS Image**
5. In the wizard, select **New Image**
6. Click **Browse** and locate your Cisco IOS .bin / .image file
7. GNS3 will ask to **decompress** the image — click **Yes** (improves performance)
8. Click **Next**

**Step 3: Configure Router Settings**\
Fill in the details (depending on your particular need for the experiment):\
**Field Example Value**\
**Name** Cisco 3725\
**Platform** c3725 (match your IOS image)\
**RAM** 128 MB (default; increase if needed)\
Click **Next**\
**Step 4: Set Idle-PC Value**\
This is **critical** — without it, the router will consume 100% CPU.

1. Click **Idle-PC finder** and wait for GNS3 to calculate a value
2. Select a value marked with an asterisk \* (best candidates)
3. Click **OK** → **Finish**\
   **Step 5: Add the Router to a Topology**
4. Close Preferences
5. In the **Device Panel** on the left, find your router under **Routers**
6. Drag it onto the **canvas**
7. Right-click → **Start** to boot it
8. Right-click → **Console** to open the CLI\
   **Step 6: Verify It's Working**\
   In the console, you should see Cisco IOS booting. Once done:\
   Router> enable\
   Router# show version\
   This confirms IOS is running correctly.

**Important Tips to consider:**\
● **Recommended IOS images for GNS3:** c3725, c3745, c7200 are most commonly used\
and well-supported\
● **GNS3 VM:** For better performance, run the GNS3 VM (via VMware or VirtualBox) and\
connect it to your local GNS3 — router images run inside the VM\
● **Cisco VIRL/CML images:** If you have access to Cisco Modeling Labs, those images\
(IOSv, IOSvL2) integrate more cleanly with GNS\
● **IOU/IOL:** Cisco IOS on Unix is another option for lighter emulation
