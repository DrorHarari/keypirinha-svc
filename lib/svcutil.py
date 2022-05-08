#
# Utility function for working with the WIN32 APIs for Services
#

import ctypes as ct
import sys

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


class SERVICE_CONTROL_STATUS_REASON_PARAMS(ct.Structure):
    _fields_ = [
        ("reason", ct.c_ulong),
        ("comment", ct.c_char_p),
        ("service_status", SERVICE_STATUS_PROCESS)
    ]


class WinServiceUtils:
    # Service types
    ST_SERVICE_DRIVER               = 0x0000000B
    ST_SERVICE_FILE_SYSTEM_DRIVER   = 0x00000002
    ST_SERVICE_KERNEL_DRIVER        = 0x00000001
    ST_SERVICE_WIN32                = 0x00000030
    ST_SERVICE_WIN32_OWN_PROCESS    = 0x00000010
    ST_SERVICE_WIN32_SHARE_PROCESS  = 0x00000020

    # Service states for enumeration
    SS_SERVICE_ACTIVE       = 0x00000001
    SS_SERVICE_INACTIVE     = 0x00000002
    SS_SERVICE_STATE_ALL    = 0x00000003

    # Service States for CurrentState
    SERVICE_START_PENDING    = 0x00000002
    SERVICE_STOPPED          = 0x00000001
    SERVICE_STOP_PENDING     = 0x00000003
    SERVICE_RUNNING          = 0x00000004
    SERVICE_CONTINUE_PENDING = 0x00000005
    SERVICE_PAUSE_PENDING    = 0x00000006
    SERVICE_PAUSED           = 0x00000007

    # Service accepted controls
    SERVICE_ACCEPT_STOP           = 0x00000001
    SERVICE_ACCEPT_PAUSE_CONTINUE = 0x00000002

    # Service control manager access options
    SC_MANAGER_CONNECT            = 0x0001
    SC_MANAGER_ENUMERATE_SERVICE  = 0x0004
    SC_MANAGER_ALL_ACCESS         = 0x000f003f

    # Service access options
    SERVICE_QUERY_CONFIG         = 0x0001
    SERVICE_CHANGE_CONFIG        = 0x0002
    SERVICE_QUERY_STATUS         = 0x0004
    SERVICE_ENUMERATE_DEPENDENTS = 0x0008
    SERVICE_START                = 0x0010
    SERVICE_STOP                 = 0x0020
    SERVICE_PAUSE_CONTINUE       = 0x0040
    SERVICE_INTERROGATE          = 0x0080
    SERVICE_USER_DEFINED_CONTROL = 0x0100

    # Service control codes
    SERVICE_CONTROL_STOP           = 0x00000001
    SERVICE_CONTROL_PAUSE          = 0x00000002
    SERVICE_CONTROL_CONTINUE       = 0x00000003
    SERVICE_CONTROL_INTERROGATE    = 0x00000004
    SERVICE_CONTROL_PARAMCHANGE    = 0x00000006
    SERVICE_CONTROL_NETBINDADD     = 0x00000007
    SERVICE_CONTROL_NETBINDREMOVE  = 0x00000008
    SERVICE_CONTROL_NETBINDENABLE  = 0x00000009
    SERVICE_CONTROL_NETBINDDISABLE = 0x0000000A

    # Windows error codes
    ERROR_INSUFFICIENT_BUFFER = 122
    GENERIC_EXECUTE           = 0x20000000
    GENERIC_WRITE             = 0x40000000
    GENERIC_READ              = 0x80000000  


    def declare_fnc(ct_dll, func_name, ret=None, args=[]):
        fnc = getattr(ct_dll, func_name)
        fnc.restype = ret
        fnc.argtypes = args
        return fnc


    _advapi32 = ct.windll.advapi32

    _OpenSCManager = declare_fnc(_advapi32, "OpenSCManagerA", ct.c_void_p,
        [ct.c_char_p, ct.c_char_p, ct.c_ulong])

    _OpenService = declare_fnc(_advapi32, "OpenServiceA", ct.c_void_p,
        [ct.c_void_p, ct.c_char_p, ct.c_ulong])

    _CloseServiceHandle = declare_fnc(_advapi32, "CloseServiceHandle", ct.c_bool,
        [ct.c_void_p])

    SC_STATUS_PROCESS_INFO = 0  # QueryServiceStatusEx level
    _QueryServiceStatusEx = declare_fnc(_advapi32, "QueryServiceStatusEx",  ct.c_bool,
        [ct.c_void_p, ct.c_ulong, ct.POINTER(SERVICE_STATUS_PROCESS), ct.c_void_p, ct.c_void_p])

    _EnumServicesStatus = declare_fnc(_advapi32, "EnumServicesStatusA", ct.c_bool,
        [ct.c_void_p, ct.c_ulong, ct.c_ulong, ct.c_char_p, ct.c_ulong, ct.c_void_p, ct.c_void_p, ct.c_void_p])

    _ControlServiceEx = declare_fnc(_advapi32, "ControlServiceExA", ct.c_bool,
        [ct.c_void_p, ct.c_ulong, ct.c_ulong, ct.POINTER(SERVICE_CONTROL_STATUS_REASON_PARAMS)])


    def __init__(self):
        pass


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
#        handle = ADVAPI32._handle
#        del ADVAPI32
#        ct.windll.kernel32.FreeLibrary(handle)
        pass


    def ServiceStateText(self, state):
        if state == self.SERVICE_STOPPED:
            return "Stopped"
        elif state == self.SERVICE_START_PENDING:
            return "Start pending"
        elif state == self.SERVICE_STOP_PENDING:
            return "Stop pending"
        elif state == self.SERVICE_RUNNING:
            return "Running"
        elif state == self.SERVICE_CONTINUE_PENDING:
            return "Continue pending"
        elif state == self.SERVICE_PAUSE_PENDING:
            return "Pause pending"
        elif state == self.SERVICE_PAUSED:
            return "Paused"
        else:
            return f"Unknown service state ({state})"


    #
    # advapi32.dll
    #
    def CloseServiceHandle(self, handle):
        return self._CloseServiceHandle(handle)


    def OpenSCManager(self, machine_name=None, database_name=None, desired_access=0):
        machine_name = bytes(machine_name, "mbcs") if machine_name else None
        database_name = bytes(database_name, "mbcs") if database_name else None
        return self._OpenSCManager(machine_name, database_name, desired_access)


    def OpenService(self, scm_h, name, desired_access=0):
        name = bytes(name, "mbcs") if name else None
        return self._OpenService(scm_h, name, desired_access)


    def WindowsError(self, text):
        return RuntimeError(f"{text}. {ct.WinError().strerror} (ct.WinError().winerror)")


    def QueryServiceStatusEx(self, name):
        scm_h = self.OpenSCManager(None, None, self.SC_MANAGER_CONNECT)
        if not scm_h:
            raise self.WindowsError("Failed to open service control")

        service_h = self.OpenService(scm_h, name, self.SERVICE_QUERY_STATUS)
        if not service_h:
            self.CloseServiceHandle(scm_h)
            raise self.WindowsError(f"Failed to open service {name}")

        status = SERVICE_STATUS_PROCESS()
        buf_size = ct.sizeof(status)
        bytes_needed = ct.c_ulong(0)
        ret = self._QueryServiceStatusEx(service_h, self.SC_STATUS_PROCESS_INFO, ct.pointer(status), buf_size, ct.byref(bytes_needed))

        self.CloseServiceHandle(service_h)
        self.CloseServiceHandle(scm_h)

        if not ret:
            raise self.WindowsError(f"Failed to query status of service {name}")

        return status


    def EnumServicesStatus(self, service_type, service_state):
        scm_h = self.OpenSCManager(None, None, self.SC_MANAGER_CONNECT + self.SC_MANAGER_ENUMERATE_SERVICE)
        if not scm_h:
            raise self.WindowsError("Failed to open service control")

        buf_size = 0
        bytes_needed = ct.c_ulong(0)
        services_returned = ct.c_ulong(0)
        resume_handle = ct.c_void_p(None)
        ret = self._EnumServicesStatus(scm_h, service_type, service_state, None, buf_size, ct.byref(bytes_needed), ct.byref(services_returned), ct.byref(resume_handle))
        
        buf_size = bytes_needed.value
        service_data = ct.create_string_buffer(buf_size)
        ret = self._EnumServicesStatus(scm_h, service_type, service_state, 
            service_data, buf_size, ct.byref(bytes_needed), ct.byref(services_returned), ct.byref(resume_handle))

        if not ret:
            raise self.WindowsError("Failed to enumerate service statuses")

        svcs = ct.cast(service_data, ct.POINTER(ENUM_SERVICE_STATUS))

        self.CloseServiceHandle(scm_h)

        return { bytes.decode(svcs[i].service_name.lower(), "mbcs") : svcs[i] for i in range(services_returned.value) }


    def StopService(self, service_name):
        scm_h = self.OpenSCManager(None, None, self.SC_MANAGER_CONNECT + self.SERVICE_STOP)
        if not scm_h:
            raise self.WindowsError("Failed to open service control")

        service_h = self.OpenService(self, scm_h, service_name, self.SERVICE_STOP)
        if not service_h:
            self.CloseServiceHandle(scm_h)
            raise self.WindowsError(f"Failed to open service {service_name} with Stop access")

        reason_params = SERVICE_CONTROL_STATUS_REASON_PARAMS()

        ret = self._ControlServiceEx(scm_h, self.SERVICE_CONTROL_STOP, 1, ct.pointer(reason_params))

        self.CloseServiceHandle(service_h)
        self.CloseServiceHandle(scm_h)

        if not ret:
            raise self.WindowsError("Failed to enumerate service statuses")
