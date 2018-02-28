/*
 * This file is autogenerated from api.xml by api_codegen.py
 */
#include "memory_map.h"
#if TRAPSET_STREAM
    case IPC_SIGNAL_ID_SINK_SLACK:
    {
        const IPC_SINK_SLACK *ipc_prim = (const IPC_SINK_SLACK *)prim;
        rsp_prim.ipc_uint16_rsp.ret = vm_trap_SinkSlack
        (
            ipc_prim->sink
        );
        ipc_send(IPC_SIGNAL_ID_SINK_SLACK_RSP,
                 &rsp_prim.ipc_uint16_rsp,
                 sizeof(rsp_prim.ipc_uint16_rsp));
    }
        break;
    case IPC_SIGNAL_ID_SINK_CLAIM:
    {
        const IPC_SINK_CLAIM *ipc_prim = (const IPC_SINK_CLAIM *)prim;
        rsp_prim.ipc_uint16_rsp.ret = vm_trap_SinkClaim
        (
            ipc_prim->sink,
            ipc_prim->extra
        );
        ipc_send(IPC_SIGNAL_ID_SINK_CLAIM_RSP,
                 &rsp_prim.ipc_uint16_rsp,
                 sizeof(rsp_prim.ipc_uint16_rsp));
    }
        break;
    case IPC_SIGNAL_ID_SINK_MAP:
    {
        const IPC_SINK_MAP *ipc_prim = (const IPC_SINK_MAP *)prim;
        rsp_prim.ipc_uint8__ptr_rsp.ret = vm_trap_SinkMap
        (
            ipc_prim->sink
        );
        ipc_send(IPC_SIGNAL_ID_SINK_MAP_RSP,
                 &rsp_prim.ipc_uint8__ptr_rsp,
                 sizeof(rsp_prim.ipc_uint8__ptr_rsp));
    }
        break;
    case IPC_SIGNAL_ID_SINK_FLUSH:
    {
        const IPC_SINK_FLUSH *ipc_prim = (const IPC_SINK_FLUSH *)prim;
        rsp_prim.ipc_bool_rsp.ret = vm_trap_SinkFlush
        (
            ipc_prim->sink,
            ipc_prim->amount
        );
        ipc_send(IPC_SIGNAL_ID_SINK_FLUSH_RSP,
                 &rsp_prim.ipc_bool_rsp,
                 sizeof(rsp_prim.ipc_bool_rsp));
    }
        break;
    case IPC_SIGNAL_ID_SINK_FLUSH_HEADER:
    {
        const IPC_SINK_FLUSH_HEADER *ipc_prim = (const IPC_SINK_FLUSH_HEADER *)prim;
        rsp_prim.ipc_bool_rsp.ret = vm_trap_SinkFlushHeader
        (
            ipc_prim->sink,
            ipc_prim->amount,
#ifdef CHIP_DEF_P1_SQIF_SHALLOW_SLEEP_WA_B_195036
            MEMORY_MAP_ADJUST_CONST_P1_P0(ipc_prim->header_, const void *)
#else
            ipc_prim->header_
#endif /* CHIP_DEF_P1_SQIF_SHALLOW_SLEEP_WA_B_195036 */
            ,
            ipc_prim->length
        );
        ipc_send(IPC_SIGNAL_ID_SINK_FLUSH_HEADER_RSP,
                 &rsp_prim.ipc_bool_rsp,
                 sizeof(rsp_prim.ipc_bool_rsp));
    }
        break;
    case IPC_SIGNAL_ID_SOURCE_SIZE:
    {
        const IPC_SOURCE_SIZE *ipc_prim = (const IPC_SOURCE_SIZE *)prim;
        rsp_prim.ipc_uint16_rsp.ret = vm_trap_SourceSize
        (
            ipc_prim->source
        );
        ipc_send(IPC_SIGNAL_ID_SOURCE_SIZE_RSP,
                 &rsp_prim.ipc_uint16_rsp,
                 sizeof(rsp_prim.ipc_uint16_rsp));
    }
        break;
    case IPC_SIGNAL_ID_SOURCE_SIZE_HEADER:
    {
        const IPC_SOURCE_SIZE_HEADER *ipc_prim = (const IPC_SOURCE_SIZE_HEADER *)prim;
        rsp_prim.ipc_uint16_rsp.ret = vm_trap_SourceSizeHeader
        (
            ipc_prim->source
        );
        ipc_send(IPC_SIGNAL_ID_SOURCE_SIZE_HEADER_RSP,
                 &rsp_prim.ipc_uint16_rsp,
                 sizeof(rsp_prim.ipc_uint16_rsp));
    }
        break;
    case IPC_SIGNAL_ID_SOURCE_MAP:
    {
        const IPC_SOURCE_MAP *ipc_prim = (const IPC_SOURCE_MAP *)prim;
        rsp_prim.ipc_const_uint8__ptr_rsp.ret = vm_trap_SourceMap
        (
            ipc_prim->source
        );
        ipc_send(IPC_SIGNAL_ID_SOURCE_MAP_RSP,
                 &rsp_prim.ipc_const_uint8__ptr_rsp,
                 sizeof(rsp_prim.ipc_const_uint8__ptr_rsp));
    }
        break;
    case IPC_SIGNAL_ID_SOURCE_MAP_HEADER:
    {
        const IPC_SOURCE_MAP_HEADER *ipc_prim = (const IPC_SOURCE_MAP_HEADER *)prim;
        rsp_prim.ipc_const_void__ptr_rsp.ret = vm_trap_SourceMapHeader
        (
            ipc_prim->source
        );
        ipc_send(IPC_SIGNAL_ID_SOURCE_MAP_HEADER_RSP,
                 &rsp_prim.ipc_const_void__ptr_rsp,
                 sizeof(rsp_prim.ipc_const_void__ptr_rsp));
    }
        break;
    case IPC_SIGNAL_ID_SOURCE_DROP:
    {
        const IPC_SOURCE_DROP *ipc_prim = (const IPC_SOURCE_DROP *)prim;
        vm_trap_SourceDrop
        (
            ipc_prim->source,
            ipc_prim->amount
        );
    }
        break;
    case IPC_SIGNAL_ID_SOURCE_BOUNDARY:
    {
        const IPC_SOURCE_BOUNDARY *ipc_prim = (const IPC_SOURCE_BOUNDARY *)prim;
        rsp_prim.ipc_uint16_rsp.ret = vm_trap_SourceBoundary
        (
            ipc_prim->source
        );
        ipc_send(IPC_SIGNAL_ID_SOURCE_BOUNDARY_RSP,
                 &rsp_prim.ipc_uint16_rsp,
                 sizeof(rsp_prim.ipc_uint16_rsp));
    }
        break;
    case IPC_SIGNAL_ID_SOURCE_SIZE_BLOCKING:
    {
        const IPC_SOURCE_SIZE_BLOCKING *ipc_prim = (const IPC_SOURCE_SIZE_BLOCKING *)prim;
        vm_trap_SourceSizeBlocking
        (
            ipc_prim->source
        );
    }
        break;
    case IPC_SIGNAL_ID_SOURCE_IS_VALID:
    {
        const IPC_SOURCE_IS_VALID *ipc_prim = (const IPC_SOURCE_IS_VALID *)prim;
        vm_trap_SourceIsValid
        (
            ipc_prim->source
        );
    }
        break;
    case IPC_SIGNAL_ID_SINK_IS_VALID:
    {
        const IPC_SINK_IS_VALID *ipc_prim = (const IPC_SINK_IS_VALID *)prim;
        vm_trap_SinkIsValid
        (
            ipc_prim->sink
        );
    }
        break;
#endif /* TRAPSET_STREAM */

