#handlers.py

from rapidsms.contrib.handlers import KeywordHandler

help_text = {
    'aaa': 'Help for aaa',
    'bbb': 'Help for bbb',
}

class HelpHandler(KeywordHandler):
    keyword = "help"

    def help(self):
        self.respond("Allowed commands are AAA and BBB. Send HELP <command> for more help on a specific command.")

    def handle(self, text):
        text = text.strip().lower()
        if text == 'aaa':
            self.respond(help_text['aaa'])
        elif text == 'bbb':
            self.respond(help_text['bbb'])
        else:
            self.help();

