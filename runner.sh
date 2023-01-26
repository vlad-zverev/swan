set -a
. ./env/secrets.env #  BOT_TOKEN must be here
set +a
pip3.11 install -r requirements.txt
python3.11 main.py
