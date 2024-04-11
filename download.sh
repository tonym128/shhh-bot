echo "Running Model Download"
if test -f /tmp/model/ggml-$model.bin; then
  echo "Model exists."
fi
if ! test -f /usr/local/src/models/ggml-$model.bin; then
  echo "Model does not exist. Downloading"
  cp /usr/local/src/download-ggml-model.sh /tmp/
  /tmp/download-ggml-model.sh $model
fi

echo "Copy model to replace existing one"
cp /usr/local/src/ggml-$model.bin /usr/local/src/models/ggml-model.bin
echo "Complete"
