#
# Utility function for working with the WIN32 APIs for Services
#

import ctypes as ct
import sys

def declare_fnc(ct_dll, func_name, ret=None, args=[]):
    fnc = getattr(ct_dll, func_name)
    fnc.restype = ret
    fnc.argtypes = args
    return fnc

_advapi32 = ct.windll.advapi32

_OpenSCManager = declare_fnc(_advapi32, "OpenSCManagerA", ct.c_void_p,          \
    [ct.c_char_p, ct.c_char_p, ct.c_ulong])

_OpenService = declare_fnc(_advapi32, "OpenServiceA",ct.c_void_p,               \
    [ct.c_char_p, ct.c_char_p, ct.c_ulong])

class  ENUM_SERVICE_STATUS(ct.Structure):
    _fields_ = [
        ("service_name", ct.c_char_p), 
        ("display_name", ct.c_char_p), 
        ("service_status", ct.c_ulong), 
        ("service_type", ct.c_ulong),
        ("current_state", ct.c_ulong),
        ("controls_accepted", ct.c_ulong),
        ("win_exit_code", ct.c_ulong),
        ("service_exit_code", ct.c_ulong),
        ("check_point", ct.c_ulong),
        ("wait_hint", ct.c_ulong)
    ]


_EnumServicesStatus = declare_fnc(_advapi32, "EnumServicesStatusA", ct.c_bool,  \
    [ct.c_void_p, ct.c_ulong, ct.c_ulong, ct.c_char_p, ct.c_ulong, ct.c_void_p, ct.c_void_p, ct.c_void_p])


# Service types
ST_SERVICE_DRIVER 				= 0x0000000B
ST_SERVICE_FILE_SYSTEM_DRIVER	= 0x00000002
ST_SERVICE_KERNEL_DRIVER		= 0x00000001
ST_SERVICE_WIN32				= 0x00000030
ST_SERVICE_WIN32_OWN_PROCESS	= 0x00000010
ST_SERVICE_WIN32_SHARE_PROCESS	= 0x00000020

# Service states
SS_SERVICE_ACTIVE		= 0x00000001
SS_SERVICE_INACTIVE		= 0x00000002
SS_SERVICE_STATE_ALL	= 0x00000003


class WinServiceUtils:
  
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
#        handle = ADVAPI32._handle
#        del ADVAPI32
#        ct.windll.kernel32.FreeLibrary(handle)
        pass

    #
    # Kernel32.dll
    #
    def CloseHandle(self, handle):
        return ct.windll.kernel32.CloseHandle(handle)

    #
    # advapi32.dll
    #
    def OpenSCManager(self, machine_name = None, database_name = None, desired_access = 0):
        return _OpenSCManager(machine_name, database_name, desired_access)

    def OpenService(self, scmanager_h, name, desired_access = 0):
        return _OpenService(scmanager_h, name, desired_access)
    
    def get_service_info(self, s):
        return {  
            "service_name": bytes.decode(s.service_name),
            "display_name": bytes.decode(s.display_name),
            "service_status": s.service_status,
            "service_type": s.service_type,
            "current_state": s.current_state,
            "controls_accepted": s.controls_accepted,
            "win_exit_code": s.win_exit_code,
            "service_exit_code": s.service_exit_code,
            "check_point": s.check_point,
            "wait_hint": s.wait_hint,
        }

               

    def EnumServicesStatus(self, scm_handle, service_type, service_state):
        buf_size = 0
        bytes_needed = ct.c_ulong(0)
        services_returned = ct.c_ulong(0)
        resume_handle = ct.c_void_p(None)
        ret = _EnumServicesStatus(scm_handle, service_type, service_state, None, buf_size, ct.byref(bytes_needed), ct.byref(services_returned), ct.byref(resume_handle))
        
        buf_size = bytes_needed.value
        service_data = ct.create_string_buffer(buf_size)
        ret = _EnumServicesStatus(scm_handle, service_type, service_state, 
            service_data, buf_size, ct.byref(bytes_needed), ct.byref(services_returned), ct.byref(resume_handle))
        
        svcs = ct.cast(service_data, ct.POINTER(ENUM_SERVICE_STATUS))

        return { bytes.decode(svcs[i].service_name) : self.get_service_info(svcs[i]) for i in range(services_returned.value) }


        
api = WinServiceUtils()
scm = api.OpenSCManager(None,None,5)
ret = api.EnumServicesStatus(scm,0x30,0x3)
print(ret)

'''
SC_HANDLE OpenSCManagerA(
  [in, optional] LPCSTR lpMachineName,
  [in, optional] LPCSTR lpDatabaseName,
  [in]           DWORD  dwDesiredAccess
);
SC_HANDLE OpenServiceW(
  [in] SC_HANDLE hSCManager,
  [in] LPCSTR   lpServiceName,
  [in] DWORD     dwDesiredAccess
);
BOOL EnumServicesStatusA(
  [in]                SC_HANDLE              hSCManager,
  [in]                DWORD                  dwServiceType,
  [in]                DWORD                  dwServiceState,
  [out, optional]     LPENUM_SERVICE_STATUSA lpServices,
  [in]                DWORD                  cbBufSize,
  [out]               LPDWORD                pcbBytesNeeded,
  [out]               LPDWORD                lpServicesReturned,
  [in, out, optional] LPDWORD                lpResumeHandle
);
typedef struct _ENUM_SERVICE_STATUSA {
  LPSTR          lpServiceName;
  LPSTR          lpDisplayName;
  SERVICE_STATUS ServiceStatus;
} ENUM_SERVICE_STATUSA, *LPENUM_SERVICE_STATUSA;
'''
