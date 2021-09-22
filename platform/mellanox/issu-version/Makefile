.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MAIN_TARGET = issu-version
BULLSEYE_DEST = $(DEST)/../bullseye

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	sx_sdk --version | egrep -o 'ISSU [0-9]+' > $(DEST)/$(MAIN_TARGET) || {
		echo "ISSU version is undefined: $(sx_sdk --version)"
		rm $(DEST)/$(MAIN_TARGET)
		exit 1
	}
	cp $(DEST)/$(MAIN_TARGET) $(BULLSEYE_DEST)/$(MAIN_TARGET)
