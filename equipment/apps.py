from sim.operations import OperationBase
from operation_parser import gobbler
from moderation.models import *
from django.utils.translation import ugettext_noop as _

SINGLE_ALPHA = "[A-Z]"
ONE_DIGIT = "[0-9]"
TWO_DIGITS = "[0-9]\W*[0-9]"
FRIDGE_TEMP_OP_CODE = "FT"

def _top_error(results):
    return _errors(results)[0][1]

def _errors(results):
    return filter(lambda e: e[1] != None, results)

def _has_errors(results):
    return len(_errors(results)) > 0

class TooManyArgsException(Exception):
    pass

class UnrecognizedTextException(Exception):
    pass

class EquipmentBase(OperationBase):

    def _take_at_most_one_equipment_id(self, args):
        g = Gobbler(args.upper())
        equipment_id = g.gobble("[A-Z]")
        # It's okay if equipment_id is None--this is within spec.

        # Extra stuff--reject with error
        remainder = g.remainder
        if remainder:
            if equipment_id:
                error = "Message OK until %s. Provide one equipment code and nothing else. " \
                        "Please fix and send again." % (remainder[:3],)
                raise TooManyArgsException(error)
            else:
                error = "Message OK until %s. Expected an equipment code. Please fix and " \
                        "send again." % (remainder[:3],)
                raise UnrecognizedTextException(error)
            message.respond(response)

        return equipment_id

    def _respond_to_error(self, message, check_results, commit_results):
        # Send appropriate response (including the highest-priority error returned in check or commit phases)
        results = check_results + (commit_results if commit_results else [])
        if _has_errors(results):
            return str(_top_error(results))
        else:
            return "Success. Thanks for your input!"

    def _handle_any(self, message, opcode):
        args = message.fields['operations'][opcode]

        try:
            equipment_id = self._take_at_most_one_equipment_id(args)
        except (TooManyArgsException, UnrecognizedTextException) as e:
            message.respond(str(e))
            return

        check_results, commit_results = self.send_signals(message=message,
                                                          equipment_id=equipment_id)

        error = self._respond_to_error(message, check_results, commit_results)
        message.respond(str(error))

class EquipmentFailure(EquipmentBase):

    def handle(self, message):
        self._handle_any(message, "NF")

class EquipmentRepaired(EquipmentBase):

    def handle(self, message):
        self._handle_any(message, "WO")

class FridgeTemperature(OperationBase):

    def _parse_events(self, args):
        """
        Used internally to help parse the arguments for an FT message.
        Attempts to parse the number of events from the argument string.

        To support the current deployment in Laos this will try to parse a
        sigle zero or two event numbers.

        Returns a three element tuple containing:
          1) a parsing error or None if there are no errors
          2) a two element tuple containging the number of High and Low events
             or None if there was a parsing error
          3) the remaining characters from the original argument string
        """
        num_high, remaining = gobbler.gobble(ONE_DIGIT, args)

        if num_high:
            num_high = int(num_high)
            num_low, remaining = gobbler.gobble(ONE_DIGIT, remaining)
            if num_low:
                num_low = int(num_low)
                # found high and low numbers
                return None, (num_high, num_low), remaining

            if num_high == 0:
                # found single zero
                return None, (0, 0), remaining

            # did not find the expected low digit
            result_fmtstr = _("OK until: %(remaining_chars)s. Expected a number of low temperature events. " \
                                "Please fix and send again.")
            result_context = { "remaining_chars": remaining }

            parse_error = error(_("Error Parsing FT Arguments"), {}, result_fmtstr, result_context)
            return parse_error, None, remaining

        # did not find any digits
        return None, None, remaining

    def parse_arguments(self, arg_string, message):
        """
        Parses arguments during the RapidSMS parse phase. Expects messages in
        the form: FT <Alpha Tag ID> <# of High Temp Events> <# of Low Temp Events>

        To work with current Laos deployment, will also accept a single 0 in the
        place of two zeros. This is intended to save the trouble of typing 00.

        To work with current Laos deployment, will also accept the lack of a
        fridge tag if there is only one set of temperature events. This is
        intented to be used when there is only one fridge at the facility.
        """
        # look for degenerate case, missing fridge id
        parse_error, events, remaining = self._parse_events(arg_string)
        if parse_error:
            return [parse_error], {}

        if events and not remaining:
            # found events for a single fridge with no id
            result_fmtstr = _("Parsed: High Events: %(num_high)s Low Events: %(num_low)s." )
            result_context = { "num_high": events[0], "num_low": events[1] }

            effect = info(_("Parsed FT Arguments"), {}, result_fmtstr, result_context)
            return [effect], { 'fridge_events': { None: events } }

        fridge_events = dict()

        # look for a fridge id and events
        while remaining:
            fridge_id, remaining = gobbler.gobble(SINGLE_ALPHA, remaining)

            if fridge_id:
                if fridge_id in fridge_events:
                    # found a fridge id that was already in the message
                    result_fmtstr = _("OK until: %(remaining_chars)s. Duplicate Fridge ID. " \
                                        "Please fix and send again.")
                    result_context = { "remaining_chars": remaining }

                    effect = error(_("Error Parsing FT Arguments"), {}, result_fmtstr, result_context)
                    return [effect], {}

                effects, events, remaining = self._parse_events(remaining)

                if effects:
                    return [effects], {}

                if events:
                    # found the event numbers
                    fridge_events[fridge_id] = events
                else:
                    result_fmtstr = _("OK until: %(remaining_chars)s. Expected a number of high and low temperate events. " \
                                        "Please fix and send again.")
                    result_context = { "remaining_chars": remaining }

                    effect = error(_("Error Parsing FT Arguments"), {}, result_fmtstr, result_context)
                    return [effect], {}
            else:
                # didn't find a fridge id
                result_fmtstr = _("OK until: %(remaining_chars)s. Expected a fridge tag. " \
                                        "Please fix and send again.")
                result_context = { "remaining_chars": remaining }

                effect = error(_("Error Parsing FT Arguments"), {}, result_fmtstr, result_context)
                return [effect], {}

        # parsed all the args into fridge ids and numbers of events
        result_fmtstr = _("Parsed Fridge Events: %(fridge_events)s.")
        result_context = { "fridge_events": repr(fridge_events) }

        effect = info(_("Parsed FT Arguments"), {}, result_fmtstr, result_context)
        return [effect], { 'fridge_events': fridge_events }