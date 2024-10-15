from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
import subprocess
import os


class CodeWorkspaceExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        code_command = extension.preferences["code_command"]
        root_folder = extension.preferences["root_folder"]

        search_command = "find " + root_folder + " -type f -name *.code-workspace "
        
        workspaces = []
        items = []

        if event.get_argument():
            search_command += f" | grep {event.get_argument()}"
        try:
            result = subprocess.run(
                [
                    'sh',
                    '-c',
                    search_command
                ], capture_output=True, text=True, check=True)
            output = result.stdout.strip()
            if output:
                workspaces = output.split('\n')
            if len(workspaces) > 10:
                workspaces = workspaces[:10]
        except subprocess.CalledProcessError as e:
            output = f"Error: {e.stderr.strip()}"
        except FileNotFoundError:
            output = "Error: Script not found"

        # Populate items with workspace names
        for workspace in workspaces:
            if workspace:  # Ensure the workspace name is not empty
                filename = os.path.basename(workspace)
                project_folder = os.path.basename(os.path.dirname(workspace))
                items.append(ExtensionResultItem(
                    icon='images/icon.png',
                    name=filename,
                    description=f'{project_folder}/{filename}',
                    on_enter=RunScriptAction(f"{code_command} {workspace}")
                ))
                
        if not workspaces:
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name='No workspaces found',
                description='No workspaces found in the root folder',
                on_enter=HideWindowAction()
            ))

        return RenderResultListAction(items)

if __name__ == '__main__':
    CodeWorkspaceExtension().run()