import keypirinha as kp
import keypirinha_util as kpu
import os
import subprocess

class Shell(kp.Plugin):
    knownFolders = {
        "AccountPictures": r"%AppData%\Microsoft\Windows\AccountPictures",
        "AddNewProgramsFolder": r"Control Panel\All Control Panel Items\Get Programs",
        "Administrative Tools": r"%AppData%\Microsoft\Windows\Start Menu\Programs\Administrative Tools",
        "AppData": r"%AppData%",
        "Application Shortcuts": r"%LocalAppData%\Microsoft\Windows\Application Shortcuts",
        "AppsFolder": r"Applications",
        "AppUpdatesFolder": r"Installed Updates",
        "Cache": r"%LocalAppData%\Microsoft\Windows\INetCache",
        "Camera Roll": r"%UserProfile%\Pictures\Camera Roll",
        "CD Burning": r"%LocalAppData%\Microsoft\Windows\Burn\Burn",
        "ChangeRemoveProgramsFolder": r"Control Panel\All Control Panel Items\Programs and Features",
        "Common Administrative Tools": r"%ProgramData%\Microsoft\Windows\Start Menu\Programs\Administrative Tools",
        "Common AppData": r"%ProgramData%",
        "Common Desktop": r"%Public%\Desktop",
        "Common Documents": r"%Public%\Documents",
        "CommonDownloads": r"%Public%\Downloads",
        "CommonMusic": r"%Public%\Music",
        "CommonPictures": r"%Public%\Pictures",
        "Common Programs": r"%ProgramData%\Microsoft\Windows\Start Menu\Programs",
        "CommonRingtones": r"%ProgramData%\Microsoft\Windows\Ringtones",
        "Common Start Menu": r"%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup",
        "Common Startup": r"%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup",
        "Common Templates": r"%ProgramData%\Microsoft\Windows\Templates",
        "CommonVideo": r"%Public%\Videos",
        "ConflictFolder": r"Control Panel\All Control Panel Items\Sync Center\Conflicts",
        "ConnectionsFolder": r"Control Panel\All Control Panel Items\Network Connections",
        "Contacts": r"%UserProfile%\Contacts",
        "ControlPanelFolder": r"Control Panel\All Control Panel Items",
        "Cookies": r"%LocalAppData%\Microsoft\Windows\INetCookies",
        "Cookies\Low": r"%LocalAppData%\Microsoft\Windows\INetCookies\Low",
        "CredentialManager": r"%AppData%\Microsoft\Credentials",
        "CryptoKeys": r"%AppData%\Microsoft\Crypto",
        "desktop": r"Desktop",
        "device Metadata Store": r"%ProgramData%\Microsoft\Windows\DeviceMetadataStore",
        "documentsLibrary": r"Libraries\Documents",
        "downloads": r"%UserProfile%\Downloads",
        "dpapiKeys": r"%AppData%\Microsoft\Protect",
        "Favorites": r"%UserProfile%\Favorites",
        "Fonts": r"%WinDir%\Fonts",
        "Games": r"Games",
        "GameTasks": r"%LocalAppData%\Microsoft\Windows\GameExplorer",
        "History": r"%LocalAppData%\Microsoft\Windows\History",
        "HomeGroupCurrentUserFolder": r"Homegroup\(user-name)",
        "HomeGroupFolder": r"Homegroup",
        "ImplicitAppShortcuts": r"%AppData%\Microsoft\Internet Explorer\Quick Launch\User Pinned\ImplicitAppShortcuts",
        "InternetFolder": r"Internet Explorer",
        "Libraries": r"Libraries",
        "Links": r"%UserProfile%\Links",
        "Local AppData": r"%LocalAppData%",
        "LocalAppDataLow": r"%UserProfile%\AppData\LocalLow",
        "MusicLibrary": r"Libraries\Music",
        "MyComputerFolder": r"This PC",
        "My Music": r"%UserProfile%\Music",
        "My Pictures": r"%UserProfile%\Pictures",
        "My Video": r"%UserProfile%\Videos",
        "NetHood": r"%AppData%\Microsoft\Windows\Network Shortcuts",
        "NetworkPlacesFolder": r"Network",
        "OneDrive": r"OneDrive",
        "OneDriveCameraRoll": r"%UserProfile%\OneDrive\Pictures\Camera Roll",
        "OneDriveDocuments": r"%UserProfile%\OneDrive\Documents",
        "OneDriveMusic": r"%UserProfile%\OneDrive\Music",
        "OneDrivePictures": r"%UserProfile%\OneDrive\Pictures",
        "Personal": r"%UserProfile%\Documents",
        "PicturesLibrary": r"Libraries\Pictures",
        "PrintersFolder": r"All Control Panel Items\Printers",
        "PrintHood": r"%AppData%\Microsoft\Windows\Printer Shortcuts",
        "Profile": r"%UserProfile%",
        "ProgramFiles": r"%ProgramFiles%",
        "ProgramFilesCommon": r"%ProgramFiles%\Common Files",
        "ProgramFilesCommonX64": r"%ProgramFiles%\Common Files (64-bit Windows only)",
        "ProgramFilesCommonX86": r"%ProgramFiles(x86)%\Common Files (64-bit Windows only)",
        "ProgramFilesX64": r"%ProgramFiles% (64-bit Windows only)",
        "ProgramFilesX86": r"%ProgramFiles(x86)% (64-bit Windows only)",
        "Programs": r"%AppData%\Microsoft\Windows\Start Menu\Programs",
        "Public": r"%Public%",
        "PublicAccountPictures": r"%Public%\AccountPictures",
        "PublicGameTasks": r"%ProgramData%\Microsoft\Windows\GameExplorer",
        "PublicLibraries": r"%Public%\Libraries",
        "Quick Launch": r"%AppData%\Microsoft\Internet Explorer\Quick Launch",
        "Recent": r"%AppData%\Microsoft\Windows\Recent",
        "RecordedTVLibrary": r"Libraries\Recorded TV",
        "RecycleBinFolder": r"Recycle Bin",
        "ResourceDir": r"%WinDir%\Resources",
        "Ringtones": r"%ProgramData%\Microsoft\Windows\Ringtones",
        "Roamed Tile Images": r"%LocalAppData%\Microsoft\Windows\RoamedTileImages",
        "Roaming Tiles": r"%AppData%\Microsoft\Windows\RoamingTiles",
        "SavedGames": r"%UserProfile%\Saved Games",
        "Screenshots": r"%UserProfile%\Pictures\Screenshots",
        "Searches": r"%UserProfile%\Searches",
        "SearchHistoryFolder": r"%LocalAppData%\Microsoft\Windows\ConnectedSearch\History",
        "SearchHomeFolder": r"search-ms:",
        "SearchTemplatesFolder": r"%LocalAppData%\Microsoft\Windows\ConnectedSearch\Templates",
        "SendTo": r"%AppData%\Microsoft\Windows\SendTo",
        "Start Menu": r"%AppData%\Microsoft\Windows\Start Menu",
        "StartMenuAllPrograms": r"StartMenuAllPrograms",
        "Startup": r"%AppData%\Microsoft\Windows\Start Menu\Programs\Startup",
        "SyncCenterFolder": r"Control Panel\All Control Panel Items\Sync Center",
        "SyncResultsFolder": r"Control Panel\All Control Panel Items\Sync Center\Sync Results",
        "SyncSetupFolder": r"Control Panel\All Control Panel Items\Sync Center\Sync Setup",
        "System": r"%WinDir%\System32",
        "SystemCertificates": r"%AppData%\Microsoft\SystemCertificates",
        "SystemX86": r"%WinDir%\SysWOW64",
        "Templates": r"%AppData%\Microsoft\Windows\Templates",
        "ThisPCDesktopFolder": r"Desktop",
        "UsersFilesFolder": r"%UserProfile%",
        "User Pinned": r"%AppData%\Microsoft\Internet Explorer\Quick Launch\User Pinned",
        "UserProfiles": r"%HomeDrive%\Users",
        "UserProgramFiles": r"%LocalAppData%\Programs",
        "UserProgramFilesCommon": r"%LocalAppData%\Programs\Common",
        "UsersLibrariesFolder": r"Libraries",
        "VideosLibrary": r"Libraries\Videos",
        "Windows": r"%WinDir%"
    }

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
