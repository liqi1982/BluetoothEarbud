###########################################################
# Makefile generated by QMDE for CSRA68100                 
#                                                          
# Project: earbud
# Configuration: debug
# Generated: Wed 28. Feb 16:44:33 2018
#                                                          
# WARNING: Do not edit this file. Any changes will be lost 
#          when the project is rebuilt.                    
#                                                          
###########################################################

BUILD_TYPE=DEBUG
CHIP_TYPE=qcc512x_qcc302x
DBG_CORE=app/p1
DBS=
DEBUGCORE=
DEBUGTRANSPORT=
DEFAULT_LIBS=usb_early_init
DEFINES=
DEFS=__KALIMBA__ HAVE_32BIT_DATA_WIDTH INSTALL_HYDRA_LOG BLUELAB DEBUG HYDRA HYDRACORE INCLUDE_AV AV_DEBUG INCLUDE_GATT INCLUDE_HFP INCLUDE_TONES USE_BDADDR_FOR_LEFT_RIGHT INCLUDE_CHARGER CF376_CF440 INCLUDE_DFU INCLUDE_POWER_CONTROL
EXTRA_WARNINGS=FALSE
FLASH_CONFIG=..\..\64Mbit_default_flash_config.py
HW_VARIANT=CF376_CF440
IDE_CONFIG=debug
IDE_PROJECT=earbud
INCPATHS=..\..\..\..\installed_libs\include\profiles\default_qcc512x_qcc302x ..\..\..\..\installed_libs\include\firmware_qcc512x_qcc302x ..\..\..\..\installed_libs\include\firmware_qcc512x_qcc302x\app ..\..\..\..\installed_libs\include\standard C:\qtil\ADK_QCC512x_QCC302x_WIN_6.2.43\audio\kalimba\kymera\common\interface\gen\k32 ..\..\chains
LIBPATHS=..\..\..\..\installed_libs\lib\default_qcc512x_qcc302x\native ..\..\..\..\installed_libs\lib\os\qcc512x_qcc302x
LIBS=a2dp avrcp hfp connection bdaddr region vmal sdp_parse service gatt_manager gatt gatt_server gatt_gap_server chain operators cryptovm rtime system_clock input_event_manager pio_common audio_processor upgrade gaia byte_utils rwcp_server
OUTDIR=E:\TWS_Project\apps\applications\earbud\qcc512x_qcc302x\CF376_CF440
OUTPUT=aura_app_p1
OUTPUT_TYPE=EXECUTABLE
PATHS=\qcc512x_qcc302x\CF376_CF440\depend_debug_aura
PERCONFIGDEPEND=depend_debug_aura
PRESERVED_LIBS=qcc512x_qcc302x
PRIVATE_DEFS=
PRIVATE_INCPATHS=
STRIP_SYMBOLS=FALSE
SW_VARIANT=
argument=
default=
description=
devkit_group=
permission=


INPUTS=\
    ..\..\av_headset_db.db \
    ..\..\1_button.buttonxml \
    ..\..\av_headset_a2dp.c \
    ..\..\av_headset_auth.c \
    ..\..\av_headset_av.c \
    ..\..\av_headset_av_caps.c \
    ..\..\av_headset_avrcp.c \
    ..\..\av_headset_battery.c \
    ..\..\av_headset_charger.c \
    ..\..\av_headset_con_manager.c \
    ..\..\av_headset_conn_rules.c \
    ..\..\av_headset_device.c \
    ..\..\av_headset_gaia.c \
    ..\..\av_headset_gatt.c \
    ..\..\av_headset_handset_signalling.c \
    ..\..\av_headset_hfp.c \
    ..\..\av_headset_init.c \
    ..\..\av_headset_kymera.c \
    ..\..\av_headset_led.c \
    ..\..\av_headset_link_policy.c \
    ..\..\av_headset_pairing.c \
    ..\..\av_headset_peer_signalling.c \
    ..\..\av_headset_phy_state.c \
    ..\..\av_headset_power.c \
    ..\..\av_headset_scan_manager.c \
    ..\..\av_headset_sdp.c \
    ..\..\av_headset_sm.c \
    ..\..\av_headset_stubs.c \
    ..\..\av_headset_tasklist.c \
    ..\..\av_headset_test.c \
    ..\..\av_headset_ui.c \
    ..\..\av_headset_upgrade.c \
    ..\..\main.c \
    ..\..\chains\chain_aptx_mono_no_autosync_decoder.chain \
    ..\..\chains\chain_forwarding_input_aac_left.chain \
    ..\..\chains\chain_forwarding_input_aac_right.chain \
    ..\..\chains\chain_forwarding_input_aptx_left.chain \
    ..\..\chains\chain_forwarding_input_aptx_right.chain \
    ..\..\chains\chain_forwarding_input_sbc_left.chain \
    ..\..\chains\chain_forwarding_input_sbc_right.chain \
    ..\..\chains\chain_output_volume.chain \
    ..\..\chains\chain_sbc_mono_no_autosync_decoder.chain \
    ..\..\chains\chain_sco_nb.chain \
    ..\..\chains\chain_sco_nb_2mic.chain \
    ..\..\chains\chain_sco_wb.chain \
    ..\..\chains\chain_sco_wb_2mic.chain \
    ..\..\chains\chain_tone_gen.chain \
    ..\..\av_headset.h \
    ..\..\av_headset_a2dp.h \
    ..\..\av_headset_auth.h \
    ..\..\av_headset_av.h \
    ..\..\av_headset_avrcp.h \
    ..\..\av_headset_battery.h \
    ..\..\av_headset_charger.h \
    ..\..\av_headset_con_manager.h \
    ..\..\av_headset_config.h \
    ..\..\av_headset_conn_rules.h \
    ..\..\av_headset_device.h \
    ..\..\av_headset_gaia.h \
    ..\..\av_headset_gatt.h \
    ..\..\av_headset_handset_signalling.h \
    ..\..\av_headset_hfp.h \
    ..\..\av_headset_init.h \
    ..\..\av_headset_kymera.h \
    ..\..\av_headset_latency.h \
    ..\..\av_headset_led.h \
    ..\..\av_headset_link_policy.h \
    ..\..\av_headset_message.h \
    ..\..\av_headset_pairing.h \
    ..\..\av_headset_peer_signalling.h \
    ..\..\av_headset_phy_state.h \
    ..\..\av_headset_power.h \
    ..\..\av_headset_role.h \
    ..\..\av_headset_scan_manager.h \
    ..\..\av_headset_sdp.h \
    ..\..\av_headset_sm.h \
    ..\..\av_headset_tasklist.h \
    ..\..\av_headset_test.h \
    ..\..\av_headset_ui.h \
    ..\..\av_headset_upgrade.h \
$(DBS)

-include earbud.mak
# Check required variables have been defined
ifdef MAKEFILE_RULES_DIR
  $(info Using $(MAKEFILE_RULES_DIR)/Makefile.rules)
  include $(MAKEFILE_RULES_DIR)/Makefile.rules
else
  ifdef SDK
    include $(SDK)/Makefile.rules
  else
    $(error Variable SDK has not been defined. It should be set to the location of the Devkit tools folder.)
  endif
endif