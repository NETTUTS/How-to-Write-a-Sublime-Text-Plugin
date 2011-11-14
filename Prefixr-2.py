import sublime
import sublime_plugin
import urllib
import urllib2
import threading


class PrefixrCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # We check for braces since we can do a better job of preserving
        # whitespace when braces are not present
        braces = False
        sels = self.view.sel()
        for sel in sels:
            if self.view.substr(sel).find('{') != -1:
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

        # We start one thread per selection so we don't lock up the interface
        # while waiting for the response from the API
        threads = []
        for sel in sels:
            string = self.view.substr(sel)
            thread = PrefixrApiCall(sel, string, 5)
            threads.append(thread)
            thread.start()

        # We clear all selection because we are going to manually set them
        self.view.sel().clear()

        # This creates an edit group so we can undo all changes in one go
        edit = self.view.begin_edit('prefixr')

        self.handle_threads(edit, threads, braces)


class PrefixrApiCall(threading.Thread):
    def __init__(self, sel, string, timeout):
        self.sel = sel
        self.original = string
        self.timeout = timeout
        self.result = None
        threading.Thread.__init__(self)

    def run(self):
        try:
            data = urllib.urlencode({'css': self.original})
            request = urllib2.Request('http://prefixr.com/api/index.php', data,
                headers={"User-Agent": "Sublime Prefixr"})
            http_file = urllib2.urlopen(request, timeout=self.timeout)
            self.result = http_file.read()
            return

        except (urllib2.HTTPError) as (e):
            err = '%s: HTTP error %s contacting API' % (__name__, str(e.code))
        except (urllib2.URLError) as (e):
            err = '%s: URL error %s contacting API' % (__name__, str(e.reason))

        sublime.error_message(err)
        self.result = False
