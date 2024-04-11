echo "Running Model Download"
model=/models/ggml-"$SHHH_WHISPER_MODEL".bin
echo $model

if test -f "$model"; then
  echo "Model exists."
else
  echo "Model does not exist. Downloading"
  cp ./models/download-ggml-model.sh /models/download-ggml-model.sh
  /models/download-ggml-model.sh "$SHHH_WHISPER_MODEL"
fi

if ! cmp -s "$model" /usr/local/src/models/ggml-model.bin; then
    echo "Link model to whisper one"
    ln -s $model /usr/local/src/models/ggml-model.bin
    echo "Complete"
fi
