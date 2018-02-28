/****************************************************************************
Copyright (c) 2017 Qualcomm Technologies International, Ltd.

FILE NAME
    audio_voice_common_dsp.c

DESCRIPTION
    Implementation of DSP operations.
*/

#include <audio.h>
#include <audio_voice_common.h>
#include <audio_mixer.h>
#include <audio_plugin_common.h>
#include <audio_plugin_ucid.h>
#include <audio_ports.h>
#include <print.h>
#include <resource_manager.h>
#include <string.h>
#include <operators.h>

#include "audio_voice_common_config.h"
#include "audio_voice_common_dsp.h"
#include "audio_voice_common_messages.h"

#define AEC_MIC_INPUT_A         (0)
#define AEC_MIC_INPUT_B         (1)

#define NB_SAMPLE_RATE      (8000)
#define WB_SAMPLE_RATE      (16000)


/******************************************************************************/
void AudioVoiceCommonDspPowerOff(void)
{
    OperatorsFrameworkDisable();
}

/*******************************************************************************
DESCRIPTION
    Create all the operators required for the SEND/RECEIVE audio voice chain.
*/
static void createOperators(audio_voice_context_t* ctx, operator_filters_t* filter)
{
    Operator cvc_send_op;
    Operator cvc_rcv_op;
    const chain_config_t* config = AudioVoiceCommonGetChainConfig(ctx);
    kymera_chain_handle_t chain = PanicNull(ChainCreateWithFilter(config, filter));

    ctx->chain = chain;

    cvc_send_op = ChainGetOperatorByRole(chain, cvc_send_role);
    cvc_rcv_op  = ChainGetOperatorByRole(chain, cvc_receive_role);

    if(cvc_send_op)
        OperatorsStandardSetUCID(cvc_send_op, ucid_cvc_send);

    if(cvc_rcv_op)
        OperatorsStandardSetUCID(cvc_rcv_op, ucid_cvc_recv);

    ChainConnect(chain);
}

/******************************************************************************/
static bool connectSource(audio_voice_context_t* ctx)
{
    audio_mixer_connect_t connect_data;
    audio_mixer_input_t mixer_input;
    uint16 sample_rate = (ctx->encoder == link_encoding_msbc) ? WB_SAMPLE_RATE : NB_SAMPLE_RATE;

    Sink rcv_sink = ChainGetInput(ctx->chain, stream_receive);
    Source rcv_source = ChainGetOutput(ctx->chain, stream_receive);

    if(StreamConnect(ctx->audio_source, rcv_sink) == NULL)
        return FALSE;

    connect_data.left_src = rcv_source;
    connect_data.right_src = (Source)NULL;
    connect_data.connection_type = CONNECTION_TYPE_VOICE;
    connect_data.sample_rate = sample_rate;
    connect_data.channel_mode = CHANNEL_MODE_STEREO;
    connect_data.variable_rate = FALSE;
   
    mixer_input = AudioMixerConnect(&connect_data);
    PanicFalse(mixer_input != audio_mixer_input_error_none);
    ctx->mixer_input = mixer_input;

    return TRUE;
}

/*******************************************************************************
DESCRIPTION
    Configure and connect a microphone.
*/
static void connectMic(Source mic_source, unsigned aec_mic_input)
{
    if(mic_source)
    {
        Sink aec_ref_mic = AudioPortsGetAecMicInput(aec_mic_input);
        PanicNull(StreamConnect(mic_source, aec_ref_mic));
    }
}

/*******************************************************************************
DESCRIPTION
    Callback from the resource_manager to inform this plugin when another
    plugin has requested or released a resource.
    
    Currently this plugin will never release the voice mic until it has 
    finished with it. Any other plugin will have to wait.
*/
static bool rmCallback(rm_msg_id_t msg, rm_resource_id_t res)
{
    bool ret = TRUE;

    switch (msg)
    {
    case rm_msg_release_req:
        {
            if (res == rm_resource_voice_mic)
                ret = FALSE;
        }
        break;

    case rm_msg_available_ind:
        {
            ret = FALSE;
        }
        break;

    default:
        ret = FALSE;
    }

    return ret;
}

/*******************************************************************************
DESCRIPTION
    Connect a microphones configured to use internal routing, which means
    either ADC or digital microphones.
*/
static void connectMicrophones(audio_voice_context_t *ctx)
{
    const voice_mic_params_t* mics = ctx->mic_params;
    uint32 sample_rate = AudioMixerGetOutputSampleRate(CONNECTION_TYPE_VOICE, ctx->incoming_sample_rate);

    Source mic_source_b = NULL;
    Source mic_source_a = AudioPluginMicSetup(AUDIO_CHANNEL_A, mics->mic_a, sample_rate);

    if(ctx->two_mic)
    {
        /* Configure microphone B */
        mic_source_b = AudioPluginMicSetup(AUDIO_CHANNEL_B, mics->mic_b, sample_rate);

        /* Synchronise both microphones A and B */
        SourceSynchronise(mic_source_a, mic_source_b);
    }

    connectMic(mic_source_a, AEC_MIC_INPUT_A);
    connectMic(mic_source_b, AEC_MIC_INPUT_B);
}

/*******************************************************************************
DESCRIPTION
    Connect AEC REFERENCE to the voice send operators.
*/
static void connectAecReference(audio_voice_context_t* ctx)
{
    Sink send_aec_ref = ChainGetInput(ctx->chain, stream_aec_ref);
    Sink send_in1 = ChainGetInput(ctx->chain, stream_send_mic1);
    Sink send_in2 = ChainGetInput(ctx->chain, stream_send_mic2);

    if(send_aec_ref)
        PanicNull(StreamConnect(AudioPortsGetAecReference(), send_aec_ref));

    PanicNull(StreamConnect(AudioPortsGetAecOutputTerminal(0), send_in1));

    if(ctx->two_mic && send_in2)
    {
        PanicNull(StreamConnect(AudioPortsGetAecOutputTerminal(1), send_in2));
    }
}

/*******************************************************************************
DESCRIPTION
    Connect sink to the microphone path
*/
static bool connectSink(audio_voice_context_t* ctx)
{
    Source send_out = ChainGetOutput(ctx->chain, stream_send_mic1);
    return (StreamConnect(send_out, ctx->audio_sink) != NULL);
}

/*******************************************************************************
DESCRIPTION
    Start processing
*/
static void startChain(Task task, audio_voice_context_t* ctx)
{
    ChainStart(ctx->chain);

    AudioMixerFadeIn(ctx->mixer_input, task);
}

/******************************************************************************/
void AudioVoiceCommonDspCreateChainAndFadeIn(Task task, audio_voice_context_t* ctx, operator_filters_t* filters)
{

    PanicFalse(rm_status_success == ResourceManagerAcquireResource(rm_resource_voice_mic, rmCallback));
    createOperators(ctx, filters);
    if(connectSource(ctx))
    {
        connectMicrophones(ctx);
        if(connectSink(ctx))
        {
            connectAecReference(ctx);
            startChain(task, ctx);
            return;
        }
    }

    /* Connection failed, tear everything down and indicate error */
    MessageSend(task, AUDIO_VOICE_CONNECT_ERROR, NULL);
}

/******************************************************************************/
void AudioVoiceCommonDspFadeOut(Task task)
{
    AudioMixerFadeOut(audio_mixer_input_voice, task);
}

/*******************************************************************************
DESCRIPTION
    Disconnect microphones.
*/
static void disconnectMicrophones(audio_voice_context_t *ctx)
{
    AudioPluginMicShutdown(AUDIO_CHANNEL_A, &ctx->mic_params->mic_a, TRUE);

    if(ctx->two_mic)
    {
        AudioPluginMicShutdown(AUDIO_CHANNEL_B, &ctx->mic_params->mic_b, TRUE);
    }
}

/*******************************************************************************
DESCRIPTION
    Stop processing
*/
static void stopChain(audio_voice_context_t *ctx)
{
    if(ctx->chain)
        ChainStop(ctx->chain);
}

/*******************************************************************************
DESCRIPTION
    Destroy the chain
*/
static void destroyChain(audio_voice_context_t *ctx)
{
    if(ctx->chain)
        ChainDestroy(ctx->chain);

    ctx->chain = NULL;
}

/******************************************************************************/
void AudioVoiceCommonDspDestroyChain(audio_voice_context_t* ctx)
{
    stopChain(ctx);

    if(ctx->mixer_input != audio_mixer_input_error_none)
        AudioMixerDisconnect(ctx->mixer_input);

    disconnectMicrophones(ctx);

    /* Disconnect the source and sink ports */
    StreamDisconnect(ctx->audio_source, NULL);
    StreamDisconnect(NULL, ctx->audio_sink );

    destroyChain(ctx);
    
    ResourceManagerReleaseResource(rm_resource_voice_mic, rmCallback);
}
