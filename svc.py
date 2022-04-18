import keypirinha as kp
import keypirinha_util as kpu
from .svcutil import *
import os

class Svc(kp.Plugin):
    # Categories
    ITEMCAT_SVC     = kp.ItemCategory.USER_BASE + 1         # 1001
    ITEMCAT_RUNNING = kp.ItemCategory.USER_BASE + 2         # 1002
    ITEMCAT_STOPPED = kp.ItemCategory.USER_BASE + 3         # 1003
    ITEMCAT_PAUSED  = kp.ItemCategory.USER_BASE + 4         # 1004

    # Plugin actions
    ITEMACT_START    = "start"
    ITEMACT_STOP     = "stop"
    ITEMACT_RESTART  = "restart"
    ITEMACT_PAUSE    = "pause"
    ITEMACT_RESUME   = "resume"
    
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

#    def on_events(self, flags):
#        if flags & kp.Events.PACKCONFIG:
#            self.on_catalog()
        
    def on_catalog(self):
        self._service_catalog = self._wsu.EnumServicesStatus(0x30, 0x3)

        catalog = [
            self.create_item(
                    category = kp.ItemCategory.REFERENCE,
                    label = "Svc",
                    short_desc = "Work with Windows services",
                    target = "Svc",
                    args_hint = kp.ItemArgsHint.REQUIRED,
                    hit_hint = kp.ItemHitHint.NOARGS)
        ]

        self.set_catalog(catalog)
       
        start_action = self.create_action(name=self.ITEMACT_START, label="Start", short_desc="Start service")
        stop_action = self.create_action(name=self.ITEMACT_STOP, label="Stop", short_desc="Stop service")
        restart_action = self.create_action(name=self.ITEMACT_RESTART, label="Restart", short_desc="Restart service")
        pause_action = self.create_action(name=self.ITEMACT_PAUSE, label="Pause", short_desc="Pause service")
        resume_action = self.create_action(name=self.ITEMACT_RESUME, label="Resume", short_desc="Resume service")

        self.set_actions(self.ITEMCAT_RUNNING, [stop_action, restart_action, pause_action])
        self.set_actions(self.ITEMCAT_STOPPED, [start_action, restart_action, resume_action])
        self.set_actions(self.ITEMCAT_PAUSED, [stop_action, resume_action, restart_action])

    def set_service_category(self, user_input, items_chain):
        item = items_chain[-1]
        service_name = item.target()
        suggestions = []

        service_status = self._wsu.QueryServiceStatusEx(service_name)

        if service_status.current_state in [self._wsu.SERVICE_RUNNING]:
            suggestions.append(
                self.create_item(
                        category = self.ITEMCAT_RUNNING,
                        label = f"Running service {service_name}",
                        short_desc = "Running service",
                        target = service_name,
                        args_hint = kp.ItemArgsHint.FORBIDDEN,
                        hit_hint = kp.ItemHitHint.NOARGS))
        elif service_status.current_state in [self._wsu.SERVICE_STOPPED]:
            suggestions.append(
                self.create_item(
                        category = self.ITEMCAT_STOPPED,
                        label = f"Stopped service {service_name}",
                        short_desc = "Stopped service",
                        target = service_name,
                        args_hint = kp.ItemArgsHint.FORBIDDEN,
                        hit_hint = kp.ItemHitHint.NOARGS))


# SERVICE_STOPPED         
# SERVICE_START_PENDING           suggestions = []
# SERVICE_STOP_PENDING            suggestions.append(
# SERVICE_RUNNING                     self.create_item(
# SERVICE_CONTINUE_PENDING                    category = self.ITEMCAT_ACTION,
# SERVICE_PAUSE_PENDING                       label = f"Start service {service_name}",
# SERVICE_PAUSED                              short_desc = "Start service",
                    # target = "start",
                    # args_hint = kp.ItemArgsHint.FORBIDDEN,
                    # hit_hint = kp.ItemHitHint.NOARGS))
        # suggestions.append(
            # self.create_item(
                    # category = self.ITEMCAT_ACTION,
                    # label = f"Stop service {service_name}",
                    # short_desc = "Stop service",
                    # target = "stop",
                    # args_hint = kp.ItemArgsHint.FORBIDDEN,
                    # hit_hint = kp.ItemHitHint.NOARGS))

        self.set_suggestions(suggestions, kp.Match.ANY, kp.Sort.NONE)


    
    def on_suggest(self, user_input, items_chain):
        if not items_chain:
            return

        current_item = items_chain[-1]

        if items_chain and items_chain[-1].category() == self.ITEMCAT_SVC:
            self.set_service_category(user_input, items_chain)
            return
        elif not current_item.category() == kp.ItemCategory.REFERENCE and not user_input:
            return

        if user_input is None or len(user_input) < -1:
            return
        else:
            user_input = user_input.lower()

        suggestions = []
        for (service_name, service) in self._service_catalog.items():
            if user_input.lower() in service_name:
                suggestions.append(self.create_item(
                    category=self.ITEMCAT_SVC,
                    label=f'Service {service_name}',
                    short_desc=bytes.decode(service.display_name, "mbcs"),
                    target=service_name,
                    loop_on_suggest = True,
                    args_hint=kp.ItemArgsHint.FORBIDDEN,
                    hit_hint=kp.ItemHitHint.IGNORE))

        self.set_suggestions(suggestions, kp.Match.ANY, kp.Sort.NONE)

    def on_execute(self, item, action):
        if not item:
            return

        print(f"target={item.target()}, category={item.category()}")
        #startup_info = subprocess.STARTUPINFO()
        #sub = subprocess.Popen(f"explorer shell:{item.target()}", startupinfo=startup_info)
