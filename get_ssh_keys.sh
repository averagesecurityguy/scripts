#/bin/bash

KEY_DIR=keys;

if [ ! -d "$KEY_DIR" ]; then
    mkdir $KEY_DIR;
    cd $KEY_DIR;
else
    echo "The '$KEY_DIR' directory already exists. Quitting.";
    exit;
fi

i=1;
for f in $(grep -R "BEGIN RSA PRIVATE KEY" /home/* | cut -d':' -f1); do
    cp $f ssh_key-$i;
    i=$((i+1))
done

