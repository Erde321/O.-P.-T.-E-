---

# **O.P.T.E. (Online Platform for Tabletop RPGs)**  
*Open-source self-hosted platform for playing Tabletop RPGs online*

O.P.T.E. is an open-source, self-hosted web platform designed for playing tabletop role-playing games (TTRPGs) online. It enables users to easily manage campaigns, characters, NPCs, and maps, while allowing sharing of entire campaigns through `.erde` files. The platform uses **ngrok** for port forwarding, making it accessible outside your local network.

O.P.T.E. also allows users to extend the platform's functionality by integrating custom logic written in Python.

### **Key Features:**
- **Customizable Campaign Management**: Manage entire campaigns, including characters, NPCs, maps, and notes.
- **Character Sheets**: Create, track, and update detailed character sheets for your TTRPG characters.
- **Custom Maps**: Upload and use your own maps in your campaigns with interactive features.
- **NPC Management**: Create and manage NPCs, their stats, and their interactions with players.
- **Campaign Sharing**: Easily share entire campaigns by exporting them as `.erde` files, which contain all relevant data such as characters, maps, NPCs, and notes.
- **Python Integration**: Extend and modify the platform’s logic by adding custom Python scripts to integrate your own features or game mechanics.
- **Simple Setup**: With just `make start`, you can run the platform without hassle.

### **System Requirements:**
- **Linux**: The platform is designed to run natively on Linux.
- **Windows (via WSL)**: Windows users can run the platform using **Windows Subsystem for Linux (WSL)**.
- **ngrok**: Used for port forwarding to make your platform accessible from outside your local network.
- **Python**: Python is used for extending platform functionality with custom logic.

### **Getting Started:**

#### **Prerequisites:**
- Linux-based system or Windows with WSL.
- **ngrok** installed for port forwarding.
- **Make** utility installed.
- **Python 3.x** for running custom logic.

#### **Installation:**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/opt-e.git
   cd opt-e
   ```

2. **Install dependencies:**
   Follow the instructions in `install_dependencies.sh` to install all necessary libraries and dependencies.

3. **Start the server:**
   Run the following command to start the platform:
   ```bash
   make start
   ```

   This will:
   - Start the web server.
   - Set up **ngrok** for port forwarding, making your platform accessible outside your local network.

4. **Access the web platform:**
   Once the server is running, ngrok will provide a public URL to access the platform from anywhere.

#### **Uploading Maps:**
To upload a custom map:
- Navigate to the "Maps" section in the web interface.
- Click "Upload Map" and select your image file.

#### **Creating Character Sheets:**
To create new character sheets:
- Go to the "Character Sheets" section.
- Click "Create New Character" and fill in the details.

#### **Campaign Sharing:**
To share a campaign:
- Navigate to the "Campaigns" section.
- Click "Export Campaign" to generate a `.erde` file that contains all relevant campaign data.
- Share the `.erde` file with others, who can import it into their own O.P.T.E. instance.

### **Python Integration:**

O.P.T.E. allows users to extend the platform's functionality by integrating custom Python logic. To add your own features:

1. Create a new Python script and place it in the `custom_logic/` directory.
2. Define your custom logic or game mechanics within the script.
3. Modify the `config.py` to register and load your Python script when starting the platform.

This feature provides flexibility for developers who wish to create custom features, such as automated events, dice rolling mechanics, or even complex game systems.

---

### **Contributing:**

We welcome contributions to O.P.T.E.! If you want to improve the platform or add new features, feel free to fork the repository and submit a pull request.

For bug reports or feature requests, please open an issue on GitHub.

---

### **License:**
This project is licensed under the **GNU General Public License v2 (GPL-2)**. See the [LICENSE](LICENSE) file for more details.

---
