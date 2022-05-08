import keypirinha as kp
import keypirinha_util as kpu
import subprocess
from .svcutil import *
import os

class Svc(kp.Plugin):
    # Categories
    ITEMCAT_SVCACTION = kp.ItemCategory.USER_BASE + 1         # 1001

    # Plugin actions
    ITEMACT_START    = "start"
    ITEMACT_STOP     = "stop"
    ITEMACT_RESTART  = "restart"
    ITEMACT_PAUSE    = "pause"
    ITEMACT_RESUME   = "resume"
    ITEMACT_STATUS   = "status"
    
    _service_catalog = {}
    _wsu = None


    def __init__(self):
        super().__init__()

        self._wsu = WinServiceUtils()

    def on_start(self):
        pass
                
    def on_activated(self):
        pass

    def on_deactivated(self):
        pass

    def on_events(self, flags):
        if flags & kp.Events.PACKCONFIG:
            self.on_catalog()
        
    def on_catalog(self):
        self._service_catalog = self._wsu.EnumServicesStatus(0x30, 0x3)

        # catalog = [
            # self.create_item(
                    # category = kp.ItemCategory.REFERENCE,
                    # label = "Svc",
                    # short_desc = "Work with Windows services",
                    # target = "Svc",
                    # args_hint = kp.ItemArgsHint.REQUIRED,
                    # hit_hint = kp.ItemHitHint.NOARGS)
        # ]
        catalog = []
        for (service_name, service) in self._service_catalog.items():
            catalog.append(
                self.create_item(
                        category = kp.ItemCategory.REFERENCE,
                        label = f"Service {service_name}",
                        short_desc = bytes.decode(service.display_name,"mbcs"),
                        target = service_name,
                        args_hint = kp.ItemArgsHint.REQUIRED,
                        hit_hint = kp.ItemHitHint.NOARGS) )
      

        self.set_catalog(catalog)
       
 
    def start_suggestion(self, service_name):
        return self.create_item(
                        category = self.ITEMCAT_SVCACTION,
                        label = f"Start {service_name} service",
                        short_desc = "Start service",
                        target = f"{self.ITEMACT_START},{service_name}",
                        args_hint = kp.ItemArgsHint.FORBIDDEN,
                        hit_hint = kp.ItemHitHint.NOARGS)
    
    def restart_suggestion(self, service_name):
        return self.create_item(
                        category = self.ITEMCAT_SVCACTION,
                        label = f"Restart {service_name} service",
                        short_desc = "Restart service",
                        target = f"{self.ITEMACT_RESTART},{service_name}",
                        args_hint = kp.ItemArgsHint.FORBIDDEN,
                        hit_hint = kp.ItemHitHint.NOARGS)
    
    def resume_suggestion(self, service_name):
        return self.create_item(
                        category = self.ITEMCAT_SVCACTION,
                        label = f"Resume {service_name} service",
                        short_desc = "Resume service",
                        target = f"{self.ITEMACT_RESUME},{service_name}",
                        args_hint = kp.ItemArgsHint.FORBIDDEN,
                        hit_hint = kp.ItemHitHint.NOARGS)
    
    def stop_suggestion(self, service_name):
        return self.create_item(
                        category = self.ITEMCAT_SVCACTION,
                        label = f"Stop {service_name} service",
                        short_desc = "Stop service",
                        target = f"{self.ITEMACT_STOP},{service_name}",
                        args_hint = kp.ItemArgsHint.FORBIDDEN,
                        hit_hint = kp.ItemHitHint.NOARGS)
    
    def pause_suggestion(self, service_name):
        return self.create_item(
                        category = self.ITEMCAT_SVCACTION,
                        label = f"Pause {service_name} service",
                        short_desc = "Pause service",
                        target = f"{self.ITEMACT_PAUSE},{service_name}",
                        args_hint = kp.ItemArgsHint.FORBIDDEN,
                        hit_hint = kp.ItemHitHint.NOARGS)
    
    def status_suggestion(self, service_name, wsu, service_status):
        return self.create_item(
                        category = self.ITEMCAT_SVCACTION,
                        label = f"Service status: {wsu.ServiceStateText(service_status.current_state)}",
                        short_desc = f"Copy service status",
                        target = f"{self.ITEMACT_STATUS},{service_name}",
                        args_hint = kp.ItemArgsHint.FORBIDDEN,
                        hit_hint = kp.ItemHitHint.NOARGS)
    
    def on_suggest(self, user_input, items_chain):
        if not items_chain:
            return

        current_item = items_chain[-1]
        service_name = current_item.target()
        suggestions = []

        wsu = self._wsu
        service_status = wsu.QueryServiceStatusEx(service_name)

        # Add actions based on status of the service
        if service_status.controls_accepted & wsu.SERVICE_ACCEPT_STOP:
            if service_status.current_state in [wsu.SERVICE_RUNNING, wsu.SERVICE_PAUSED, wsu.SERVICE_START_PENDING, wsu.SERVICE_PAUSE_PENDING]:
                suggestions.append(self.stop_suggestion(service_name))
        if service_status.current_state in [wsu.SERVICE_STOPPED]:
            suggestions.append(self.start_suggestion(service_name))
        if service_status.controls_accepted & wsu.SERVICE_ACCEPT_PAUSE_CONTINUE:
            if service_status.current_state in [wsu.SERVICE_RUNNING]:
                suggestions.append(self.pause_suggestion(service_name))
            if service_status.current_state in [wsu.SERVICE_PAUSED]:
                suggestions.append(self.resume_suggestion(service_name))

        suggestions.append(self.status_suggestion(service_name, wsu, service_status))

        self.set_suggestions(suggestions, kp.Match.ANY, kp.Sort.NONE)

    def on_execute(self, item, kp_action):
        if not item:
            return

        print(f"on execute, target={item.target()}")
        (action, service_name) = item.target().split(",", 1)

        if action in ["start", "stop", "pause", "resume"]:
            self.service_control(action, service_name)
        elif action == "restat":
            self.service_control("stop", service_name)
        else:
            print(f"Unimplemented action <{action}> on service {service_name}")
        #startup_info = subprocess.STARTUPINFO()

    def service_control(self, command, service_name):
        """Sending control command to a service using a call to Windows' sc.exe  with elevated rights
        """
        args = ["sc.exe", command, service_name]

        self.dbg("Calling:", args)
        kpu.shell_execute(args[0], args[1:], verb="runas", show=subprocess.SW_HIDE)
