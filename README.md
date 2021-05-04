# About

This is an example client implementation written in Python to access the CyberVox platform API.

For more information, read the [API documentation](https://apidocs.cybervox.ai/).

# Getting Started

To run the example implementation:

```console
python3 -mvenv venv
source ./venv/bin/activate
pip install -r requirements.txt

export CLIENT_ID=< provided client id >
export CLIENT_SECRET=< provided client secret >

# complete API
python main.py

# text-to-speech only
python tts.py "olá mundo"

# speech-to-text only
python stt.py ola-mundo.wav
```

# Usage

```console
pydoc3 cybervox
```
