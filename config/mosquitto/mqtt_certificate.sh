#!/usr/bin/env bash
set -euo pipefail

CERT_DIR="config/mosquitto/certs"
NEW_DIR="config/mosquitto/certs-new"
SUBJ_BASE="/C=CH/ST=Switzerland/L=Lausanne/O=ELIMS/OU=IoT"
SUBJ_CA="${SUBJ_BASE}/CN=ELIMS-CA"
SUBJ_SERVER="${SUBJ_BASE}/CN=mosquitto"
SUBJ_BACKEND="${SUBJ_BASE}/CN=elims-backend-subscriber"

mkdir -p "${NEW_DIR}"

openssl genrsa -out "${NEW_DIR}/ca.key" 4096
openssl req -x509 -new -nodes -key "${NEW_DIR}/ca.key" -sha256 -days 825 -subj "${SUBJ_CA}" -out "${NEW_DIR}/ca.crt"

openssl genrsa -out "${NEW_DIR}/server.key" 2048
openssl req -new -key "${NEW_DIR}/server.key" -subj "${SUBJ_SERVER}" -out "${NEW_DIR}/server.csr"
CLIENT_EXT_FILE="${NEW_DIR}/client.ext"
SERVER_EXT_FILE="${NEW_DIR}/server.ext"

cat "${CERT_DIR}/server.ext" > "${SERVER_EXT_FILE}"
cat >> "${SERVER_EXT_FILE}" <<'EOF'
[v3_server]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names
EOF

cat > "${CLIENT_EXT_FILE}" <<'EOF'
[v3_client]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth
EOF

openssl x509 -req -in "${NEW_DIR}/server.csr" -CA "${NEW_DIR}/ca.crt" -CAkey "${NEW_DIR}/ca.key" -CAcreateserial -out "${NEW_DIR}/server.crt" -days 825 -sha256 -extfile "${SERVER_EXT_FILE}" -extensions v3_server

openssl genrsa -out "${NEW_DIR}/elims-backend-subscriber.key" 2048
openssl req -new -key "${NEW_DIR}/elims-backend-subscriber.key" -subj "${SUBJ_BACKEND}" -out "${NEW_DIR}/elims-backend-subscriber.csr"
openssl x509 -req -in "${NEW_DIR}/elims-backend-subscriber.csr" -CA "${NEW_DIR}/ca.crt" -CAkey "${NEW_DIR}/ca.key" -CAcreateserial -out "${NEW_DIR}/elims-backend-subscriber.crt" -days 825 -sha256 -extfile "${CLIENT_EXT_FILE}" -extensions v3_client

if [ "$#" -gt 0 ]; then
	for device in "$@"; do
		client_cn="${SUBJ_BASE}/CN=${device}"
		openssl genrsa -out "${NEW_DIR}/${device}.key" 2048
		openssl req -new -key "${NEW_DIR}/${device}.key" -subj "${client_cn}" -out "${NEW_DIR}/${device}.csr"
		openssl x509 -req -in "${NEW_DIR}/${device}.csr" -CA "${NEW_DIR}/ca.crt" -CAkey "${NEW_DIR}/ca.key" -CAcreateserial -out "${NEW_DIR}/${device}.crt" -days 825 -sha256 -extfile "${CLIENT_EXT_FILE}" -extensions v3_client
	done
fi

echo "Created certificates in ${NEW_DIR}."
echo "Backend client cert: ${NEW_DIR}/elims-backend-subscriber.crt"
echo "If you provided device IDs, their certs are in ${NEW_DIR}."
echo "To use them, copy server.crt/server.key/ca.crt to ${CERT_DIR} and restart mosquitto."
