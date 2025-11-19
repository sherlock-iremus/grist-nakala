python3 -m venv venv
source ./venv/bin/activate
pip3 install lxml rdflib requests pyaml
pip3 install --upgrade pip
cd python-packages/sherlock-grist-to-crm && pip3 install -e . && cd ../..
cd python-packages/grist-api-helpers && pip3 install -e . && cd ../..