#/bin/bash

HERE=`dirname $0`

if [ -d "$HERE/.venv" ]; then
    $HERE/.venv/bin/python $HERE/main.py
else
    virtualenv $HERE/.venv
    $HERE/.venv/bin/pip install -r $HERE/requirements.txt
fi

cp -v $HERE/index.html /var/www/tieba/zhaopin
cp -v $HERE/data.json /var/www/tieba/zhaopin
