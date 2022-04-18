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

_OpenService = declare_fnc(_advapi32, "OpenServiceA", ct.c_void_p,              \
    [ct.c_void_p, ct.c_char_p, ct.c_ulong])

_CloseServiceHandle = declare_fnc(_advapi32, "CloseServiceHandle", ct.c_bool,   \
    [ct.c_void_p])

class SERVICE_STATUS_PROCESS(ct.Structure):
    _fields_ = [
        ("service_type", ct.c_ulong),
        ("current_state", ct.c_ulong),
        ("controls_accepted", ct.c_ulong),
        ("win_exit_code", ct.c_ulong),
        ("service_exit_code", ct.c_ulong),
        ("check_point", ct.c_ulong),
        ("wait_hint", ct.c_ulong),
        ("process_id", ct.c_ulong),
        ("service_flags", ct.c_ulong)
    ]


SC_STATUS_PROCESS_INFO = 0  # QueryServiceStatusEx level 
_QueryServiceStatusEx = declare_fnc(_advapi32, "QueryServiceStatusEx",  ct.c_bool,  \
    [ct.c_void_p, ct.c_ulong, ct.POINTER(SERVICE_STATUS_PROCESS), ct.c_void_p, ct.c_void_p])
#    [ct.c_void_p, ct.c_ulong, ct.c_char_p, ct.c_void_p, ct.c_void_p])

class ENUM_SERVICE_STATUS(ct.Structure):
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

# Service control access options
SC_MANAGER_CONNECT              = 0x0001
SC_MANAGER_ENUMERATE_SERVICE    = 0x0004
SC_MANAGER_ALL_ACCESS           = 0x000f003f

# Windows error codes
ERROR_INSUFFICIENT_BUFFER   = 122
GENERIC_EXECUTE             = 0x20000000
GENERIC_WRITE               = 0x40000000
GENERIC_READ                = 0x80000000

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
    # advapi32.dll
    #
    def CloseServiceHandle(self, handle):
        return _CloseServiceHandle(handle)

    def OpenSCManager(self, machine_name = None, database_name = None, desired_access = 0):
        machine_name = bytes(machine_name, "mbcs") if machine_name else None
        database_name = bytes(database_name, "mbcs") if database_name else None
        return _OpenSCManager(machine_name, database_name, desired_access)

    def OpenService(self, scm_h, name, desired_access = 0):
        name = bytes(name, "mbcs") if name  else None
        return _OpenService(scm_h, name, desired_access)
    
    def WindowsError(self, text):
        return RuntimeError(f"{text}. {ct.WinError().strerror} (ct.WinError().winerror)")

    def get_service_status(self, s):
        return {  
            "service_type": s.service_type,
            "current_state": s.current_state,
            "controls_accepted": s.controls_accepted,
            "win_exit_code": s.win_exit_code,
            "service_exit_code": s.service_exit_code,
            "check_point": s.check_point,
            "wait_hint": s.wait_hint,
            "process_id": s.process_id,
            "service_flags": s.service_flags
        }

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

    def QueryServiceStatusEx(self, name):
        scm_h = self.OpenSCManager(None, None, SC_MANAGER_ALL_ACCESS) #SC_MANAGER_CONNECT+SC_MANAGER_ENUMERATE_SERVICE+GENERIC_READ)
        if not scm_h:
            raise self.WindowsError("Failed to open service control")

        service_h = self.OpenService(scm_h, name,SC_MANAGER_ALL_ACCESS)
        if not service_h:
            raise self.WindowsError(f"Failed to open service {name}")

        status = SERVICE_STATUS_PROCESS()
        buf_size = ct.sizeof(status)
        bytes_needed = ct.c_ulong(0)
        ret = _QueryServiceStatusEx(service_h, SC_STATUS_PROCESS_INFO, ct.pointer(status), buf_size, ct.byref(bytes_needed))
        if not ret:
            raise self.WindowsError(f"Failed to query status of service {name}")

        self.CloseServiceHandle(service_h)
        self.CloseServiceHandle(scm_h)

        return status
        
    def EnumServicesStatus(self, service_type, service_state):
        scm_h = self.OpenSCManager(None, None, SC_MANAGER_CONNECT+SC_MANAGER_ENUMERATE_SERVICE)

        buf_size = 0
        bytes_needed = ct.c_ulong(0)
        services_returned = ct.c_ulong(0)
        resume_handle = ct.c_void_p(None)
        ret = _EnumServicesStatus(scm_h, service_type, service_state, None, buf_size, ct.byref(bytes_needed), ct.byref(services_returned), ct.byref(resume_handle))
        
        buf_size = bytes_needed.value
        service_data = ct.create_string_buffer(buf_size)
        ret = _EnumServicesStatus(scm_h, service_type, service_state, 
            service_data, buf_size, ct.byref(bytes_needed), ct.byref(services_returned), ct.byref(resume_handle))

        svcs = ct.cast(service_data, ct.POINTER(ENUM_SERVICE_STATUS))

        self.CloseServiceHandle(scm_h)

        return { bytes.decode(svcs[i].service_name) : self.get_service_info(svcs[i]) for i in range(services_returned.value) }



'''
BOOL CloseServiceHandle(
  [in] SC_HANDLE hSCObject
);
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

BOOL QueryServiceStatusEx(
  [in]            SC_HANDLE      hService,
  [in]            SC_STATUS_TYPE InfoLevel,
  [out, optional] LPBYTE         lpBuffer,
  [in]            DWORD          cbBufSize,
  [out]           LPDWORD        pcbBytesNeeded
);


'''

