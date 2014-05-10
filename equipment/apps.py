from sim.operations import OperationBase, filter_by_opcode

from operation_parser.gobbler import *

SINGLE_ALPHA = "[A-Z]"
ONE_DIGIT = "[0-9]"
TWO_DIGITS = "[0-9]{2}"
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
        equipment_id, remaining = gobble("[A-Z]", args.upper())
        # It's okay if equipment_id is None--this is within spec.

        # Extra stuff--reject with error
        if remaining:
            if equipment_id:
                error = "Message OK until %s. Provide one equipment code and nothing else. " \
                        "Please fix and send again." % (remaining[:3],)
                raise TooManyArgsException(error)
            else:
                error = "Message OK until %s. Expected an equipment code. Please fix and " \
                        "send again." % (remaining[:3],)
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

    @filter_by_opcode
    def handle(self, message):
        self._handle_any(message, "NF")

class EquipmentRepaired(EquipmentBase):

    @filter_by_opcode
    def handle(self, message):
        self._handle_any(message, "WO")

class FridgeTemperature(OperationBase):

    def _parse_events(args):
        events, remaining = gobbler.gobble(TWO_DIGITS, args)

        if events:
            num_high = int(events[0])
            num_low  = int(events[1])

            # found high and low numbers without a fridge id
            return (num_high, num_low)

        # look for degenerate case, missing fridge id and one 0
        events, remaining = gobbler.gobble(ONE_DIGIT, args)

        if events:
            num_high = int(events)
            if num_high == 0:
                # found high without fridgeid or low
                return (0, 0)

            else:
                error = "OK until: %s. Expected a number of low temperature events. " \
                            "Please fix and send again." % remaining
                raise UnrecognizedTextException(error)

        # didn't find any event numbers
        return None

    def _parse_args(args):
        # look for degenerate case, missing fridge id
        events = parse_events(args)

        if events:
            # found events for a single fridge with no id
            return { None: events }

        fridge_events = dict()

        # look for a fridge id and events
        while remaining:
            fridge_id, remaining = gobbler.gobble(SINGLE_ALPHA, remaining)
            if fridge_id:
                if fridge_id in fridge_events:
                    # found a fridge id that was already in the message
                    error = "OK until: %s. Duplicate Fridge ID. " \
                                "Please fix and send again." % remaining
                    raise UnrecognizedTextException(error)

                events = parse_events(remaining)
                if events:
                    # found the event numbers
                    fridge_events[fridge_id] = events
                else:
                    error = "OK until: %s. Expected a number of high and low temperate events. " \
                                "Please fix and send again." % remaining
                    raise UnrecognizedTextException(error)
            else:
                # didn't find a fridge id
                error = "OK until: %s. Expected a Fridge ID. " \
                            "Please fix and send again." % remaining
                raise UnrecognizedTextException(error)

        # parsed all the args into fridge ids and numbers of events
        return fridge_events

    @filter_by_opcode
    def handle(self, message):
        # parse args
        args = message.fields['operations'][FRIDGE_TEMP_OP_CODE]

        try:
            fridge_events = parse_args(args)
        except (UnrecognizedTextException) as e:
            # TODO needs to support i18n and error format
            message.errors = str(e)
            return

        # send signals
        check_results, commit_results = self.send_signals(message=message,
                                                          fridge_events=fridge_events)
        # collect errors
        message.errors = self.select_errors(check_results, commit_results)