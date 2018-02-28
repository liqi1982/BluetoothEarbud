/*
    Warning - this file was autogenerated by genparse
    DO NOT EDIT - any changes will be lost
*/

#ifndef HFP_PARSE_H
#define HFP_PARSE_H

#include <message_.h>

#if (defined __XAP__ || defined __KALIMBA__)
#include <source.h>
#endif

const uint8 *parseData(const uint8 *s, const uint8 *e, Task task);
void handleUnrecognised(const uint8 *data, uint16 length, Task task);

#if (defined __XAP__ || defined __KALIMBA__)
uint16 parseSource(Source rfcDataIncoming, Task task);
#endif

struct sequence
{
  const uint8 *data;
  uint16 length;
};

struct value_hfpCsrFeaturesHandleModifyIndicatorsInd_p
{
  uint16 ind;
  uint16 val;
};
struct region_hfpCsrFeaturesHandleModifyIndicatorsInd_p
{
  uint16 count;
  const uint8 *s;
  const uint8 *e;
  uint16 next;
  const uint8 *next_s;
};
struct value_hfpCsrFeaturesHandleModifyIndicatorsInd_p get_hfpCsrFeaturesHandleModifyIndicatorsInd_p(const struct region_hfpCsrFeaturesHandleModifyIndicatorsInd_p*, uint16);

struct value_hfpHandleBindInfo_indicators
{
  uint16 indicator;
};
struct region_hfpHandleBindInfo_indicators
{
  uint16 count;
  const uint8 *s;
  const uint8 *e;
  uint16 next;
  const uint8 *next_s;
};
struct value_hfpHandleBindInfo_indicators get_hfpHandleBindInfo_indicators(const struct region_hfpHandleBindInfo_indicators*, uint16);

struct value_hfpHandleCallHoldInfoRange_p
{
  uint16 lower;
  uint16 upper;
};
struct region_hfpHandleCallHoldInfoRange_p
{
  uint16 count;
  const uint8 *s;
  const uint8 *e;
  uint16 next;
  const uint8 *next_s;
};
struct value_hfpHandleCallHoldInfoRange_p get_hfpHandleCallHoldInfoRange_p(const struct region_hfpHandleCallHoldInfoRange_p*, uint16);

struct value_hfpHandleCallHoldInfo_p
{
  struct sequence n;
};
struct region_hfpHandleCallHoldInfo_p
{
  uint16 count;
  const uint8 *s;
  const uint8 *e;
  uint16 next;
  const uint8 *next_s;
};
struct value_hfpHandleCallHoldInfo_p get_hfpHandleCallHoldInfo_p(const struct region_hfpHandleCallHoldInfo_p*, uint16);

struct value_hfpHandleIndicatorStatus_d
{
  uint16 n;
};
struct region_hfpHandleIndicatorStatus_d
{
  uint16 count;
  const uint8 *s;
  const uint8 *e;
  uint16 next;
  const uint8 *next_s;
};
struct value_hfpHandleIndicatorStatus_d get_hfpHandleIndicatorStatus_d(const struct region_hfpHandleIndicatorStatus_d*, uint16);

struct hfpHandleCurrentCallsWithNumber
{
  uint16 dir;
  uint16 idx;
  struct sequence ignore;
  uint16 mode;
  uint16 mprty;
  struct sequence number;
  uint16 status;
  uint16 type;
};
struct hfpHandleCurrentCalls
{
  uint16 dir;
  uint16 idx;
  struct sequence ignore;
  uint16 mode;
  uint16 mprty;
  uint16 status;
};
struct hfpHandleResponseWbsCodec
{
  uint16 codec;
};
struct hfpCsrFeaturesHandleModifyIndicatorsInd
{
  struct region_hfpCsrFeaturesHandleModifyIndicatorsInd_p p;
};
struct hfpHandleMicrophoneGain
{
  uint16 gain;
};
struct hfpHandleSpeakerGain
{
  uint16 gain;
};
struct hfpHandleBindIndicatorStatus
{
  uint16 assignedId;
  uint16 state;
};
struct hfpHandleBindInfo
{
  struct region_hfpHandleBindInfo_indicators indicators;
};
struct hfpHandleDataResponse
{
  struct sequence num;
};
struct hfpHandleDataResponseExtended
{
  struct sequence ignore;
  struct sequence num;
};
struct hfpHandleSupportedFeaturesInd
{
  uint16 supportedfeat;
};
struct hfpHandleInBandRingTone
{
  uint16 enable;
};
struct hfpHandleResponseHold
{
  uint16 state;
};
struct hfpHandleVoiceRecognitionStatus
{
  uint16 enable;
};
struct hfpHandleCallWaitingNotificationWithName
{
  uint16 class;
  struct sequence ignore;
  struct sequence name;
  struct sequence num;
  uint16 type;
};
struct hfpHandleCallWaitingNotification
{
  struct sequence ignore;
  struct sequence num;
  uint16 type;
};
struct hfpHandleCallWaitingNotificationIllegal
{
  struct sequence ignore;
  struct sequence num;
};
struct hfpHandleCallHoldInfoRange
{
  struct region_hfpHandleCallHoldInfoRange_p p;
};
struct hfpHandleCallHoldInfo
{
  struct region_hfpHandleCallHoldInfo_p p;
};
struct hfpHandleIndicatorStatusUpdate
{
  uint16 index;
  uint16 value;
};
struct hfpHandleIndicatorStatus
{
  struct region_hfpHandleIndicatorStatus_d d;
};
struct hfpHandleIndicatorList
{
  struct sequence str;
};
struct hfpHandleCallerIdWithName
{
  struct sequence ignore;
  struct sequence name;
  struct sequence num;
  struct sequence saddr;
  struct sequence satype;
  uint16 type;
};
struct hfpHandleCallerId
{
  struct sequence ignore;
  struct sequence num;
  uint16 type;
};
struct hfpHandleCallerIdIllegal
{
  struct sequence ignore;
  struct sequence num;
};
struct hfpHandleSubscriberNumber
{
  struct sequence alpha;
  struct sequence number;
  uint16 service;
  struct sequence speed;
  uint16 type;
};
struct hfpHandleNetworkOperatorModeName
{
  uint16 format;
  uint16 mode;
  struct sequence operator;
};
struct hfpHandleNetworkOperatorMode
{
  struct sequence ignore;
  uint16 mode;
};
struct hfpHandleNull
{
  struct sequence str;
};
struct hfpCsrFeaturesHandleBandwidthCodecRes
{
  uint16 battlevel;
  uint16 callername;
  uint16 codecbandwidths;
  uint16 codecs;
  struct sequence ignore;
  uint16 pwrsource;
  uint16 rawtext;
  uint16 sms;
};
struct hfpCsrFeaturesHandleCodecRes
{
  uint16 battlevel;
  uint16 callername;
  uint16 codecs;
  struct sequence ignore;
  uint16 pwrsource;
  uint16 rawtext;
  uint16 sms;
};
struct hfpCsrFeaturesHandleNormalRes
{
  uint16 battlevel;
  uint16 callername;
  struct sequence ignore;
  uint16 pwrsource;
  uint16 rawtext;
  uint16 sms;
};
struct hfpCsrFeaturesHandleSmsInd
{
  struct sequence ignore;
  struct sequence senderName;
  struct sequence senderNum;
  uint16 smsIndex;
};
struct hfpCsrFeaturesHandleTextInd
{
  struct sequence text;
};
struct hfpHandleExtendedError
{
  uint16 err;
};
struct hfpCsrFeaturesHandleGetSmsRes
{
  struct sequence sms;
};
void hfpHandleOk(Task );
void hfpHandleError(Task );
void hfpHandleRing(Task );
void hfpHandleInBandRingToneDisable(Task );
void hfpHandleInBandRingToneEnable(Task );
void hfpHandleCallHoldInfoCommon(Task );
void hfpHandleCurrentCallsWithNumber(Task , const struct hfpHandleCurrentCallsWithNumber *);
void hfpHandleCurrentCalls(Task , const struct hfpHandleCurrentCalls *);
void hfpHandleResponseWbsCodec(Task , const struct hfpHandleResponseWbsCodec *);
void hfpCsrFeaturesHandleModifyIndicatorsInd(Task , const struct hfpCsrFeaturesHandleModifyIndicatorsInd *);
void hfpCsrFeaturesHandleDisableIndicatorsInd(Task );
void hfpHandleMicrophoneGain(Task , const struct hfpHandleMicrophoneGain *);
void hfpHandleSpeakerGain(Task , const struct hfpHandleSpeakerGain *);
void hfpHandleBindIndicatorStatus(Task , const struct hfpHandleBindIndicatorStatus *);
void hfpHandleBindInfo(Task , const struct hfpHandleBindInfo *);
void hfpHandleDataResponse(Task , const struct hfpHandleDataResponse *);
void hfpHandleDataResponseExtended(Task , const struct hfpHandleDataResponseExtended *);
void hfpHandleSupportedFeaturesInd(Task , const struct hfpHandleSupportedFeaturesInd *);
void hfpHandleInBandRingTone(Task , const struct hfpHandleInBandRingTone *);
void hfpHandleResponseHold(Task , const struct hfpHandleResponseHold *);
void hfpHandleVoiceRecognitionStatus(Task , const struct hfpHandleVoiceRecognitionStatus *);
void hfpHandleCallWaitingNotificationWithName(Task , const struct hfpHandleCallWaitingNotificationWithName *);
void hfpHandleCallWaitingNotification(Task , const struct hfpHandleCallWaitingNotification *);
void hfpHandleCallWaitingNotificationIllegal(Task , const struct hfpHandleCallWaitingNotificationIllegal *);
void hfpHandleCallHoldInfoRange(Task , const struct hfpHandleCallHoldInfoRange *);
void hfpHandleCallHoldInfo(Task , const struct hfpHandleCallHoldInfo *);
void hfpHandleIndicatorStatusUpdate(Task , const struct hfpHandleIndicatorStatusUpdate *);
void hfpHandleIndicatorStatus(Task , const struct hfpHandleIndicatorStatus *);
void hfpHandleIndicatorList(Task , const struct hfpHandleIndicatorList *);
void hfpHandleCallerIdWithName(Task , const struct hfpHandleCallerIdWithName *);
void hfpHandleCallerId(Task , const struct hfpHandleCallerId *);
void hfpHandleCallerIdIllegal(Task , const struct hfpHandleCallerIdIllegal *);
void hfpHandleSubscriberNumber(Task , const struct hfpHandleSubscriberNumber *);
void hfpHandleNetworkOperatorModeName(Task , const struct hfpHandleNetworkOperatorModeName *);
void hfpHandleNetworkOperatorMode(Task , const struct hfpHandleNetworkOperatorMode *);
void hfpHandleNull(Task , const struct hfpHandleNull *);
void hfpCsrFeaturesHandleBandwidthCodecRes(Task , const struct hfpCsrFeaturesHandleBandwidthCodecRes *);
void hfpCsrFeaturesHandleCodecRes(Task , const struct hfpCsrFeaturesHandleCodecRes *);
void hfpCsrFeaturesHandleNormalRes(Task , const struct hfpCsrFeaturesHandleNormalRes *);
void hfpCsrFeaturesHandleSmsInd(Task , const struct hfpCsrFeaturesHandleSmsInd *);
void hfpCsrFeaturesHandleTextInd(Task , const struct hfpCsrFeaturesHandleTextInd *);
void hfpHandleExtendedError(Task , const struct hfpHandleExtendedError *);
void hfpCsrFeaturesHandleBatteryLevelRequestInd(Task );
void hfpCsrFeaturesHandleGetSmsRes(Task , const struct hfpCsrFeaturesHandleGetSmsRes *);
void hfpHandleNoCarrierInd(Task );

#endif
