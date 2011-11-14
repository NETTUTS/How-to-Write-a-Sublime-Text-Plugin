import sublime
import sublime_plugin


class PrefixrCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # We check for braces since we can do a better job of preserving
        # whitespace when braces are not present
        braces = False
        sels = self.view.sel()
        for sel in sels:
            if self.view.substr(sels[0]).find('{') != -1:
                braces = True

        # Expand selection to braces, unfortunately this can't use the
        # built in move_to brackets since that matches parentheses also
        if not braces:
            new_sels = []
            for sel in sels:
                new_sels.append(self.view.find('\}', sel.end()))
            sels.clear()
            for sel in new_sels:
                sels.add(sel)
            self.view.run_command("expand_selection", {"to": "brackets"})
