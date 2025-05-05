![Docker Pulls](https://img.shields.io/docker/pulls/wafy80/acestream)
![Docker Image Size](https://img.shields.io/docker/image-size/wafy80/acestream)
![Docker Build](https://github.com/wafy80/acestream/actions/workflows/image-build.yml/badge.svg)

# AceStream Docker Image

This Docker image allows you to run AceStream in a container, simplifying the installation and use of the software.

## Requirements
- **Docker** installed on your system.
- A stable network connection for P2P streaming.

## How to use the Docker image
### Starting the container
Run the following command to start the container:
```bash
docker run -d -p 6878:6878 wafy80/acestream
```

### Accessing the stream
After starting the container, you can use the following URL in your preferred media player (e.g., VLC):
```
http://<host_address>:6878/ace/getstream?id=<content_id>
```
Replace `<host_address>` with the IP address or hostname of the system running the container and `<content_id>` with the ID of the content you want to play.

## Exposed ports
- **6878**: HTTP port for accessing the web interface and video streams.
- **8621 (optional)**: UDP port used for P2P traffic (if needed, it must be manually configured in the container).

## Advanced configuration
### Running with additional ports
If you want to expose the UDP port 8621 to improve P2P performance, you can run the container with the following command:
```bash
docker run -d -p 6878:6878 -p 8621:8621/udp wafy80/acestream
```

### Customizing parameters
You can add additional parameters to the `CMD` command to configure AceStream. For example:
```bash
docker run -d -p 6878:6878 wafy80/acestream --client-console --bind-all --max-peers=50
```

## Monitoring the container
You can check the status of the AceStream service using the integrated `HEALTHCHECK` command:
```bash
wget -q -t1 -O- 'http://127.0.0.1:6878/webui/api/service?method=get_version'
```

## Useful resources
- [AceStream Official Website](https://acestream.org)
- [Docker Hub Repository](https://hub.docker.com/r/wafy80/acestream)
- [GitHub Actions Workflow](https://github.com/wafy80/acestream/actions/workflows/image-build.yml)

## Contributing
If you want to contribute to this project, feel free to open a pull request or report issues in the [Issues](https://github.com/wafy80/acestream/issues) section.

## License
This project is distributed under the **WTFPL** license. See the `LICENSE` file for more details.