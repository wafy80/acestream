![Docker Pulls](https://img.shields.io/docker/pulls/wafy80/acestream)
![Docker Image Size](https://img.shields.io/docker/image-size/wafy80/acestream)
![Docker Build](https://github.com/wafy80/acestream/actions/workflows/image-build.yml/badge.svg)
[![pages-build-deployment](https://github.com/wafy80/acestream/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/wafy80/acestream/actions/workflows/pages/pages-build-deployment)

# 🚀 AceStream Docker Image
Stream your favorite P2P content effortlessly with AceStream in a lightweight Docker container. No setup hassle—just run and play!

## 🌟 Features
- **Easy Setup**: Start streaming in seconds with a single command.
- **Lightweight**: Minimal image size for fast deployment.
- **Customizable**: Configure ports and parameters to suit your needs.
- **Compatible**: Works seamlessly with media players like VLC.

## 🛠 Requirements
- **Docker** installed on your system.
- A stable internet connection for smooth P2P streaming.

## 🚀 Quick Start
Run the following command to start the container:
```bash
docker run -d -p 6878:6878 wafy80/acestream
```

### 🎥 Access Your Stream
Use this URL in your favorite media player (e.g., VLC):
```
http://<host_address>:6878/ace/getstream?id=<content_id>
```
Replace `<host_address>` with your system's IP or hostname and `<content_id>` with the content ID you want to stream.

## 🔌 Exposed Ports
- **6878**: HTTP port for the web interface and video streams.
- **8621 (optional)**: UDP port for P2P traffic (improves performance).

## ⚙️ Advanced Configuration
### Enable UDP for Better Performance
Expose the UDP port 8621 with this command:
```bash
docker run -d -p 6878:6878 -p 8621:8621/udp wafy80/acestream
```

### Customize Parameters
Add custom parameters to configure AceStream:
```bash
docker run -d -p 6878:6878 wafy80/acestream --client-console --bind-all --max-peers=50
```

## 📊 Monitor the Service
Check the status of AceStream with this command:
```bash
wget -q -t1 -O- 'http://127.0.0.1:6878/webui/api/service?method=get_version'
```

## 🔗 Useful Links
- [AceStream Official Website](https://acestream.org)
- [Docker Hub Repository](https://hub.docker.com/r/wafy80/acestream)
- [GitHub Project](https://github.com/wafy80/acestream)

## 🤝 Contribute
Have ideas or found an issue? Open a pull request or report it in the [Issues](https://github.com/wafy80/acestream/issues) section.

## 📜 License
This project is distributed under the **WTFPL** license. See the `LICENSE` file for more details.

---

🎉 **Start streaming now and enjoy the power of AceStream in Docker!**
