from utils.operations import OperationBase
from operation_parser.gobbler import Gobbler, gobble, LABEL
from moderation.models import info, error
from django.utils.translation import ugettext_noop as _

SINGLE_ALPHA = "[A-Z]"
ONE_DIGIT = "[0-9]"
TWO_DIGITS = "[0-9]\W*[0-9]"

class EquipmentBase(OperationBase):
    '''
    A base class for Equipment SMS APIs that defines useful methods for
    handling the parse stage of those operations.
    '''

    def _ok(self, opcode, args):
        '''Return a MessageEffect that indicates success.'''
        return info(
            _("Parsed %(op_code)s Arguments"), { 'op_code': opcode },
            _("Parsed: equipment_id is %(equipment_id)s."), args
        )

    def _error_extra_chars(self, opcode):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments having extra chars after the equipment_id.
        '''
        return error(
            _("Error Parsing %(op_code)s Arguments"), { 'op_code': opcode },
            _("Text after equipment ID not allowed."), {}
        )

    def _error_unrecognized_chars(self, opcode):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments containing unrecognized characters in the argument string
        instead of an equipment_id.
        '''
        return error(
            _("Error Parsing %(op_code)s Arguments"), { 'op_code': opcode },
            _("Should start with equipment ID."), {}
        )

    def _error_no_equipment_id(self, opcode):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments being empty.
        '''
        return error(
            _("Error Parsing %(op_code)s Arguments"), { 'op_code': opcode },
            _("Must provide an equipment ID."), {}
        )

    def parse_arguments(self, opcode, arg_string, message):
        '''
        Implements OperationBase.parse_arguments.
        '''
        args = {}
        effects = []

        g = Gobbler(arg_string.upper())

        equipment_id = g.gobble(LABEL)
        args['equipment_id'] = equipment_id

        if equipment_id:
            if g.remainder:
                args, effect = None, self._error_extra_chars(opcode)
            else:
                args, effect = args, self._ok(opcode, args)
        else:
            if g.remainder:
                args, effect = None, self._error_unrecognized_chars(opcode)
            else:
                args, effect = None, self._error_no_equipment_id(opcode)
        effects.append(effect)

        return (effects, args)

class EquipmentFailure(EquipmentBase):
    '''Implements the EquipmentFailure SMS API.'''

    helptext = "For example, %(opcode)s A. Reports to managers that equipment A is broken."

class EquipmentRepaired(EquipmentBase):
    '''Implements the EquipmentRepaired SMS API.'''

    helptext = "For example, %(opcode)s A. Reports to managers that equipment A has been repaired."

class FridgeTemperature(OperationBase):
    """Implements the FridgeTemperate SMS API"""

    helptext = "For example, %(opcode)s A 1 0. Reports that fridge A had 1 high- and 1 low-temperature event, and any other fridges had none of either."

    def _error_missing_digits(self, opcode):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments missing numbers after the fridge tag.
        '''
        return error(
            _("Error Parsing %(op_code)s Arguments"), { 'op_code': opcode },
            _("Expected the number of temperature events."), {}
        )

    def _error_duplicate_fridge(self, opcode):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments having duplicate fridge tags.
        '''
        return error(
            _("Error Parsing %(op_code)s Arguments"), { 'op_code': opcode },
            _("Duplicate fridge tag."), {}
        )

    def _error_missing_fridge_tag(self, opcode):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments haveing numbers with missing fridge tags.
        '''
        return error(
            _("Error Parsing %(op_code)s Arguments"), { 'op_code': opcode },
            _("Expected a fridge tag."), {}
        )

    def _ok(self, opcode, args):
        '''Return a MessageEffect that indicates success.'''

        # Translate {fridge_id: [hi, lo], ...} to human-readable, non-repr form.
        events = args['fridge_events']
        if None in events:
            events = '%s high and %s low events' % events[None]
        else:
            to_s = lambda x: "%s had %s high and %s low events" % (x[0], x[1][0], x[1][1])
            events = map(to_s, events.items())
            events = ', '.join(events)

        return info(
            _("Parsed %(op_code)s Arguments"), { 'op_code': opcode },
            _("Parsed: %(fridge_events)s."), { 'fridge_events': events }
        )

    def _parse_events(self, opcode, args):
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
        num_high, remaining = gobble(ONE_DIGIT, args)

        if num_high:
            num_high = int(num_high)
            num_low, remaining = gobble(ONE_DIGIT, remaining)
            if num_low:
                num_low = int(num_low)
                # found high and low numbers
                return None, (num_high, num_low), remaining

            if num_high == 0:
                # found single zero
                return None, (0, 0), remaining

            # did not find the expected low digit
            return self._error_missing_digits(opcode), None, remaining

        # did not find any digits
        return None, None, remaining

    def parse_arguments(self, opcode, arg_string, message):
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
        parse_error, events, remaining = self._parse_events(opcode, arg_string)
        if parse_error:
            return [parse_error], {}

        if events and not remaining:
            # found events for a single fridge with no id
            parsed_args = { 'fridge_events': { None: events } }
            effect = self._ok(opcode, parsed_args)
            return [effect], parsed_args

        fridge_events = dict()

        # look for a fridge id and events
        while remaining:
            fridge_id, remaining = gobble(SINGLE_ALPHA, remaining)

            if fridge_id:
                if fridge_id in fridge_events:
                    # found a fridge id that was already in the message
                    effect = self._error_duplicate_fridge(opcode)
                    return [effect], {}

                effects, events, remaining = self._parse_events(opcode, remaining)

                if effects:
                    # errors were found parsing the number of events
                    return [effects], {}

                if events:
                    # found the event numbers
                    fridge_events[fridge_id] = events
                else:
                    # didn't find any event numbers
                    effect = self._error_missing_digits(opcode)
                    return [effect], {}
            else:
                # didn't find a fridge id
                effect = self._error_missing_fridge_tag(opcode)
                return [effect], {}

        # parsed all the args into fridge ids and numbers of events
        parsed_args = { 'fridge_events': fridge_events }
        effect = self._ok(opcode, parsed_args)
        return [effect], parsed_args