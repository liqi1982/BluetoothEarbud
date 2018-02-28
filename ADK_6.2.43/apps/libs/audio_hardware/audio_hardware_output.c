/*******************************************************************************
Copyright (c) 2017 Qualcomm Technologies International, Ltd.

FILE NAME
    audio_hardware_output.c
    
DESCRIPTION
    Defines the interconnections between the various audio hardware chains.
    
NOTES
*/

#include <panic.h>
#include <stream.h>

#include "audio_hardware_output.h"
#include "audio_hardware_aec.h"

/*******************************************************************************
DESCRIPTION
    Connect the AEC chain to the audio_output library.
*/
bool hardwareMapAecToAudioOutput(kymera_chain_handle_t chain)
{
    audio_hw_channel_role_t channel;
    bool connection_made = FALSE;
    audio_output_t output = audio_output_primary_left;
    PanicNull(chain);

    for (channel = left_channel; channel <= secondary_right_channel; channel++)
    {
        Source src = ChainGetOutput(chain, channel);
        if(src)
        {
            if(AudioOutputAddSource(src, output++))
                connection_made = TRUE;
        }
    }
    
    return connection_made;
}

/*******************************************************************************
DESCRIPTION
    Map input sources to audio output depending on the output type
*/
void hardwareMapSourcesToAudioOutput(const audio_hardware_connect_t* hw_connect_data)
{
    MAP_AUDIO_OUTPUT(hw_connect_data->primary_left, audio_output_primary_left);    
    MAP_AUDIO_OUTPUT(hw_connect_data->primary_right, audio_output_primary_right);
    MAP_AUDIO_OUTPUT(hw_connect_data->secondary_left, audio_output_secondary_left);
    MAP_AUDIO_OUTPUT(hw_connect_data->secondary_right, audio_output_secondary_right);
    MAP_AUDIO_OUTPUT(hw_connect_data->wired_sub, audio_output_wired_sub);    
    MAP_AUDIO_OUTPUT(hw_connect_data->aux_left, audio_output_aux_left);
    MAP_AUDIO_OUTPUT(hw_connect_data->aux_right, audio_output_secondary_right);
}

/*******************************************************************************
DESCRIPTION
    Connect the audio hardware inputs and AEC sources
*/
void hardwareConnectAecInputs(const audio_hardware_connect_t* hw_connect_data, kymera_chain_handle_t dest_chain)
{  
    AUDIO_CONNECT_STREAMS(hw_connect_data->primary_left, ChainGetInput(dest_chain, left_channel));
    AUDIO_CONNECT_STREAMS(hw_connect_data->primary_right, ChainGetInput(dest_chain, right_channel));
    AUDIO_CONNECT_STREAMS(hw_connect_data->secondary_left, ChainGetInput(dest_chain, secondary_left_channel));
    AUDIO_CONNECT_STREAMS(hw_connect_data->secondary_right, ChainGetInput(dest_chain, secondary_right_channel));    
}


/*******************************************************************************
DESCRIPTION
    Helper function to connect to audio output
*/
void hardwareConnectToAudioOutput(uint32 output_sample_rate)
{
    audio_output_params_t mch_params;

    memset(&mch_params, 0, sizeof(audio_output_params_t));

    mch_params.disable_resample = TRUE;
    mch_params.sample_rate = output_sample_rate;
    mch_params.transform = audio_output_tansform_connect;

    AudioOutputConnect(&mch_params);
}

/****************************************************************************
DESCRIPTION
    Helper function to map and connect to direct audio output
    If no AEC, connect mixer chain directly to audio output
*/
void hardwareConnectDirectToOutput(const audio_hardware_connect_t* hw_connect_data)
{
    hardwareMapSourcesToAudioOutput(hw_connect_data);
    hardwareConnectToAudioOutput(hw_connect_data->output_sample_rate);
}

