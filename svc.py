import keypirinha as kp
import keypirinha_util as kpu
import os
import subprocess

class Shell(kp.Plugin):


    ITEMCAT_SHELL = kp.ItemCategory.USER_BASE + 1

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
        catalog = [
            self.create_item(
                    category = kp.ItemCategory.REFERENCE,
                    label = "Shell",
                    short_desc = "Open a known Windows Shell folder",
                    target = "Shell",
                    args_hint = kp.ItemArgsHint.REQUIRED,
                    hit_hint = kp.ItemHitHint.NOARGS)
        ]

        self.set_catalog(catalog)
       
    def on_suggest(self, user_input, items_chain):
        suggestions = []

        if user_input is None or len(user_input) < -1:
            return
        else:
            user_input = user_input.lower()

        for kf in self.knownFolders:
            if user_input in kf.lower():
                suggestions.append(self.create_item(
                    category=self.ITEMCAT_SHELL,
                    label=f'Open {kf}',
                    short_desc=f'Folder: {self.knownFolders[kf]}',
                    target=kf,
                    args_hint=kp.ItemArgsHint.FORBIDDEN,
                    hit_hint=kp.ItemHitHint.IGNORE))

        self.set_suggestions(suggestions, kp.Match.ANY, kp.Sort.NONE)

    def on_execute(self, item, action):
        if not item:
            return

        startup_info = subprocess.STARTUPINFO()
        sub = subprocess.Popen(f"explorer shell:{item.target()}", startupinfo=startup_info)
