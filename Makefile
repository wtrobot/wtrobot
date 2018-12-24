
install:
	( \
        sudo dnf update -y; \
        sudo dnf install python3-opencv firefox -y; \
        pip3 install virtualenv --user; \
        virtualenv -p /usr/bin/python3 python3Env; \
        source python3Env/bin/activate; \
        pip install -r requirements.txt; \
    )
