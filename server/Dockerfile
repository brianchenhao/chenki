FROM ghcr.io/ggml-org/llama.cpp:server

WORKDIR /tmp

RUN curl -L -o model.gguf \
    https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf

EXPOSE 7860

ENV LD_LIBRARY_PATH=/app

ENTRYPOINT ["/app/llama-server"]
CMD ["-m", "/tmp/model.gguf", \
     "--host", "0.0.0.0", \
     "--port", "7860", \
     "-c", "4096", \
     "-t", "2"]
