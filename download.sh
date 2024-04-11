echo "Running Model Download"
model=/usr/local/src/models/ggml-"$SHHH_WHISPER_MODEL".bin
echo $model

if test -f "$model"; then
  echo "Model exists."
else
  echo "Model does not exist. Downloading"
  /usr/local/src/models/download-ggml-model.sh "$SHHH_WHISPER_MODEL"
fi

if ! cmp -s "$model" /usr/local/src/models/ggml-model.bin; then
    echo "Copy model to replace existing one"
    cp $model /usr/local/src/models/ggml-model.bin
    echo "Complete"
fi
