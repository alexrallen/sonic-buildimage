.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = issu-version
BULLSEYE_FILES_PATH = /sonic/target/files/bullseye

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	sx_sdk --version | egrep -o 'ISSU [0-9]+' > $(DEST)/$(MAIN_TARGET) || {
		echo "ISSU version is undefined: $(sx_sdk --version)"
		rm $(DEST)/$(MAIN_TARGET)
		exit 1
	}
	echo $(BULLSEYE_FILES_PATH)
	exit 1
	cp $(DEST)/$(MAIN_TARGET) $(BULLSEYE_FILES_PATH)/$(MAIN_TARGET)
