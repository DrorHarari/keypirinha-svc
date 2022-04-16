import keypirinha as kp
import keypirinha_util as kpu
from .svcutil import WinServiceUtils
import os

class Svc(kp.Plugin):

    ITEMCAT_SVC = kp.ItemCategory.USER_BASE + 1         # 1001
    ITEMCAT_ACTION = kp.ItemCategory.USER_BASE + 2      # 1002

    # Plugin actions
    ACTION_START = "start"
    ACTION_STOP = "stop"
    ACTION_RESTART = "restart"
    ACTION_STATUS = "status"
    ACTION_MANUAL = "start-ma"
    
    service_catalog = {}

    def __init__(self):
        super().__init__()

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
        wsu = WinServiceUtils()
        self.service_catalog = wsu.EnumServicesStatus(0x30, 0x3)

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

        actions = []
        actions.append(self.create_action(
            name="execute",
            label="Execute command",
            short_desc="Executes the selected command"
        ))
        self.set_actions(self.ITEMCAT_SVC, actions)
        self.set_actions(self.ITEMCAT_ACTION, actions)


    def add_actions(self, user_input, items_chain):
        item = items_chain[-1]
        sn = item.target()
        suggestions = []
        suggestions.append(
            self.create_item(
                    category = self.ITEMCAT_ACTION,
                    label = f"Start service {sn}",
                    short_desc = "Start service",
                    target = "start",
                    args_hint = kp.ItemArgsHint.FORBIDDEN,
                    hit_hint = kp.ItemHitHint.NOARGS))
        suggestions.append(
            self.create_item(
                    category = self.ITEMCAT_ACTION,
                    label = f"Stop service {sn}",
                    short_desc = "Stop service",
                    target = "stop",
                    args_hint = kp.ItemArgsHint.FORBIDDEN,
                    hit_hint = kp.ItemHitHint.NOARGS))

        self.set_suggestions(suggestions, kp.Match.ANY, kp.Sort.NONE)


    
    def on_suggest(self, user_input, items_chain):
        if not items_chain:
            return

        current_item = items_chain[-1]

        print(f"on_suggest {user_input} - #items = {len(items_chain)}")
        if (items_chain):
            print(f"categoey = {items_chain[-1].category()}, target={items_chain[-1].target()}")

        if items_chain and items_chain[-1].category() == self.ITEMCAT_SVC:
            self.add_actions(user_input, items_chain)
            return
        elif not current_item.category() == kp.ItemCategory.REFERENCE and not user_input:
            return

        if user_input is None or len(user_input) < -1:
            return
        else:
            user_input = user_input.lower()

        suggestions = []
        for sn in self.service_catalog:
            s = self.service_catalog[sn]
            if user_input in s["service_name"].lower():
                suggestions.append(self.create_item(
                    category=self.ITEMCAT_SVC,
                    label=f'Service {s["service_name"]}',
                    short_desc=s["display_name"],
                    target=sn,
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
