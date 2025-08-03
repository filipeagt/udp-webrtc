# Como rodar

1.Instale dependências:

    pip install -r requirements.txt
2.Inicie o Servidor:

    python server.py
3.Abra no navegador:

    http://<ip_do_servidor>:8080
4.Transmita o vídeo via GStreamer:

    gst-launch-1.0 v4l2src ! videoconvert ! x264enc tune=zerolatency ! rtph264pay ! udpsink host=<ip_do_pc> port=5000
