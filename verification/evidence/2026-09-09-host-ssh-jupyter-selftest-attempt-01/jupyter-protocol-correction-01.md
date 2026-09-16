# Jupyter protocol correction — attempt 01 retained

The collector initially assumed HTTP for the mapped 8080 endpoint. The browser returned ERR_CONNECTION_RESET. This was a collector assumption, not proof that the documented Jupyter workflow is broken. The central connection guide describes a direct HTTPS endpoint with a custom certificate. Retest 02 uses HTTPS with normal certificate verification; no certificate warning is bypassed. The documentation is used to choose the intended procedure, not as evidence that the service works. Actual browser output remains the independent observation.
