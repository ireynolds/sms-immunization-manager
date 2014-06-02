from user_registration.models import Facility
from rapidsms.apps.base import AppBase
from django.dispatch.dispatcher import receiver
from operation_parser.gobbler import Gobbler, INTEGER
from moderation.models import error, info, complete_effect, SYNTAX
from django.conf import settings
from django.utils.translation import ugettext_noop as _

class FacilityCode(AppBase):
    '''
    Implements the contextual Facility Code SMS API.
    '''

    helptext = "For example, FC 12. For this message, use facility 12 instead of the facility you're registered to."

    def _ok(self, opcode, facility_code):
        '''Return a MessageEffect that indicates success.'''
        return info(
            _("Parsed %(op_code)s Arguments"), { 'op_code': opcode },
            _("Parsed: facility code is %(facility_code)s."), { 'facility_code': facility_code }
        )

    def _error_extra_chars(self, opcode, arg_string):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments having extra chars after the facility code.
        '''
        return error(
            _("Error Parsing %(op_code)s Arguments"), { 'op_code': opcode },
            _("Text after facility code in %(arg_string)s not allowed."), { 'arg_string': arg_string }
        )

    def _error_unrecognized_chars(self, opcode, arg_string):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments containing unrecognized characters in the argument string
        instead of an facility code.
        '''
        return error(
            _("Error Parsing %(op_code)s Arguments"), { 'op_code': opcode },
            _("Should provide a facility code, not %(arg_string)s."), { 'arg_string': arg_string }
        )

    def _error_no_facility_code(self, opcode):
        '''
        Return a MessageEffect that indicates a failure as a result of
        the arguments being empty.
        '''
        return error(
            _("Error Parsing %(op_code)s Arguments"), { 'op_code': opcode },
            _("Must provide a facility code."), {}
        )

    def _urgent_invalid_facility_code(self, opcode, code):
        '''
        Return a MessageEffect that indicates a failure as a result of 
        the given facility code being invalid.
        '''
        return urgent(
            _("Error Verifying %(opcode)s Arguments"), { 'opcode': opcode },
            _("There is no facility %(code)s."), { 'code': code }
        )

    def _get_opcodes(self):
        '''
        Returns the set of operation codes associated with this operation.
        '''
        result = set()
        for opcode, appbase in settings.SIM_OPERATION_CODES.iteritems():
            if appbase == self.__class__:
                result.add(opcode)
        return result

    def _facility_from_code(self, code):
        '''
        Returns the Facility instance corresponding to the given facility code,
        or None if no such Facility exists.
        '''
        try:
            return Facility.from_code(int(code))
        except:
            return None

    def _parse_fc(self, opcode, arg_string):
        '''
        Given the arguments to the Facility Code operation, returns a pair containing the list of 
        MessageEffects and the facility code (or None if no facility code exists). 
        '''
        effects = []

        g = Gobbler(arg_string.upper())
        facility_code = g.gobble(INTEGER)
        
        if facility_code:
            if g.remainder:
                fac, effect = None, self._error_extra_chars(opcode, arg_string)
            else:
                fac = self._facility_from_code(facility_code)
                if fac:
                    effect = self._ok(opcode, facility_code)
                else: 
                    # See comment in parse() to understand why this is urgent.
                    effect = self._urgent_invalid_facility_code(opcode, code)
        else:
            if g.remainder:
                fac, effect = None, self._error_unrecognized_chars(opcode, arg_string)
            else:
                fac, effect = None, self._error_no_facility_code(opcode)
        effects.append(effect)

        return (effects, fac)

    def _find_operation(self, operations):
        '''
        If one exists, returns the index in operations of a Facility Code operation, its opcode, and
        its arguments. Returns None, None, None otherwise.
        '''
        for i in xrange(len(operations)):
            opcode, _ = operations[i]
            if opcode in self._get_opcodes():
                return i
        return None

    def parse(self, message):
        '''
        Implements the RapidSMS parse phase. Also sets message.fields['facility'] to the 
        facility context for this message.
        '''
        effects = []
        facility = None

        # If FC code is present
        index = self._find_operation(message.fields['operations'])
        if index != None:
            opcode, arg_string = message.fields['operations'][index]
            more_effects, facility = self._parse_fc(opcode, arg_string)
            for effect in more_effects:
                complete_effect(effect, message.logger_msg, SYNTAX, index, opcode)
            effects.extend(more_effects)
        
        # If FC code is not present -OR- contained an error.
        #
        # This is done even in case of error above to prevent raising exceptions while processing
        # other SMS APIs that access the message's facility.
        #
        # If the facility code exists but is invalid, then this condition will succeed. Because
        # only the first error is returned, then it may be that an earlier operation fails because
        # the FC code did, but only that one's error (the symptom, not the cause) is returned. To
        # prevent this, an error due to an invalid facility code is marked urgent to guarantee that
        # it, as well, is returned.
        if facility == None:
            facility = message.connections[0].contact.contactprofile.facility

            name = _("No Facility Code Operation") if index == None else _("Error in Facility Code Operation")
            effect = info(
                name, {},
                _("Using facility code from ContactProfile."), {}
            )
            complete_effect(effect, message.logger_msg, SYNTAX)
            effects.append(effect)

        message.fields['facility'] = facility
        message.fields['operation_effects'].extend(effects)
