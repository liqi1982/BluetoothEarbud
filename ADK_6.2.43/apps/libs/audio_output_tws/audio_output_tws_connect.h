/****************************************************************************
Copyright (c) 2017 Qualcomm Technologies International, Ltd.
Part of 6.2

FILE NAME
    audio_output_tws_connect.h

DESCRIPTION
    TWS functionality
*/

#ifndef AUDIO_OUTPUT_TWS_CONNECT_H_
#define AUDIO_OUTPUT_TWS_CONNECT_H_

void AudioOutputTwsConnect(Task output_task, const AUDIO_PLUGIN_FORWARDING_CREATE_REQ_T* req);

void AudioOutputTwsStart(Task output_task, const AUDIO_PLUGIN_FORWARDING_START_REQ_T* req);

void AudioOutputTwsStop(Task output_task, const AUDIO_PLUGIN_FORWARDING_STOP_REQ_T* req);

void AudioOutputTwsDestroy(Task output_task, const AUDIO_PLUGIN_FORWARDING_DESTROY_REQ_T* req);

void AudioOutputTwsConnectReset(void);

#endif /* AUDIO_OUTPUT_TWS_CONNECT_H_ */
