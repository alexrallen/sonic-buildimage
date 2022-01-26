#
# Copyright (c) 2016-2021 NVIDIA CORPORATION & AFFILIATES.
# Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# docker image for mlnx syncd

DOCKER_SYNCD_PLATFORM_CODE = mlnx


# Since the build template is for buster we copy it here and modify it for now
DOCKER_SYNCD_BASE_STEM = docker-syncd-$(DOCKER_SYNCD_PLATFORM_CODE)
DOCKER_SYNCD_BASE = $(DOCKER_SYNCD_BASE_STEM).gz
DOCKER_SYNCD_BASE_DBG = $(DOCKER_SYNCD_BASE_STEM)-$(DBG_IMAGE_MARK).gz

$(DOCKER_SYNCD_BASE)_PATH = $(PLATFORM_PATH)/docker-syncd-$(DOCKER_SYNCD_PLATFORM_CODE)

$(DOCKER_SYNCD_BASE)_FILES += $(SUPERVISOR_PROC_EXIT_LISTENER_SCRIPT)

$(DOCKER_SYNCD_BASE)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE_BULLSEYE)
$(DOCKER_SYNCD_BASE)_DBG_DEPENDS += $($(DOCKER_CONFIG_ENGINE_BULLSEYE)_DBG_DEPENDS)
$(DOCKER_SYNCD_BASE)_DBG_IMAGE_PACKAGES = $($(DOCKER_CONFIG_ENGINE_BULLSEYE)_DBG_IMAGE_PACKAGES)

SONIC_DOCKER_IMAGES += $(DOCKER_SYNCD_BASE)
ifneq ($(ENABLE_SYNCD_RPC),y)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SYNCD_BASE)
endif

SONIC_DOCKER_DBG_IMAGES += $(DOCKER_SYNCD_BASE_DBG)
ifneq ($(ENABLE_SYNCD_RPC),y)
SONIC_INSTALL_DOCKER_DBG_IMAGES += $(DOCKER_SYNCD_BASE_DBG)
endif

$(DOCKER_SYNCD_BASE)_CONTAINER_NAME = syncd
$(DOCKER_SYNCD_BASE)_RUN_OPT += --privileged -t
$(DOCKER_SYNCD_BASE)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SYNCD_BASE)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro

SONIC_BULLSEYE_DOCKERS += $(DOCKER_SYNCD_BASE)
SONIC_BULLSEYE_DBG_DOCKERS += $(DOCKER_SYNCD_BASE_DBG)


$(DOCKER_SYNCD_BASE)_DEPENDS += $(SYNCD) $(PYTHON_SDK_API) $(MFT)

$(DOCKER_SYNCD_BASE)_FILES += $(ISSU_VERSION_FILE)

$(DOCKER_SYNCD_BASE)_DBG_DEPENDS += $(SYNCD_DBG) \
                                $(LIBSWSSCOMMON_DBG) \
                                $(LIBSAIMETADATA_DBG) \
                                $(LIBSAIREDIS_DBG)

ifeq ($(SDK_FROM_SRC), y)
$(DOCKER_SYNCD_BASE)_DBG_DEPENDS += $(MLNX_SDK_DBG_DEBS) $(MLNX_SAI_DBGSYM)
endif

$(DOCKER_SYNCD_BASE)_VERSION = 1.0.0
$(DOCKER_SYNCD_BASE)_PACKAGE_NAME = syncd

$(DOCKER_SYNCD_BASE)_RUN_OPT += -v /host/warmboot:/var/warmboot

