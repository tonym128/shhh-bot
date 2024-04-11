echo "Running Model Download"
model=/tmp/model/ggml-"$1".bin
if test -f "$model"; then
  echo "Model exists."
else
  echo "Model does not exist. Downloading"
  cp /usr/local/src/download-ggml-model.sh /tmp/
  /tmp/download-ggml-model.sh $1
fi

echo "Copy model to replace existing one"
cp /tmp/ggml-$1.bin /usr/local/src/models/ggml-model.bin
echo "Complete"
