"""SC Controller - ActionParser

Parses action(s) expressed as string or in dict loaded from json file into
one or more Action instances.
"""

from __future__ import annotations

import sys
import token as TokenType
from tokenize import TokenError, generate_tokens
from typing import NamedTuple

from scc.actions import Action, MultiAction, NoAction, RangeOP
from scc.constants import PARSER_CONSTANTS, STICK, HapticPos, SCButtons
from scc.macros import Macro
from scc.tools import nameof
from scc.uinput import Axes, Keys, Rels


class ParseError(Exception):
    pass


def build_action_constants() -> dict:
    """Generate dicts for ActionParser.CONSTS."""
    rv = {"Keys": Keys, "Axes": Axes, "Rels": Rels, "HapticPos": HapticPos,
          "None": NoAction(), "True": True, "False": False}
    for c in PARSER_CONSTANTS:
        rv[c] = c
    for tpl in (Keys, Axes, Rels, SCButtons, HapticPos):
        for x in tpl:
            rv[x.name] = x
    for b in ("A", "B", "X", "Y", "START", "SELECT"):
        name = f"BTN_{b}"
        rv[name] = getattr(Keys, name)
    return rv


class ActionParser:
    """Parse action expressed as string into Action instances."""

    class Token(NamedTuple):
        type: int
        value: str

    CONSTS = build_action_constants()

    def __init__(self, string: str = "") -> None:
        self.restart(string)
        self.tokens: list[ActionParser.Token] | None

    def from_json_data(self, data: dict, key: str | None = None):
        if key is not None:
            if key in data:
                return self.from_json_data(data[key], None)
            return NoAction()
        a = self.restart(data["action"]).parse() or NoAction() if "action" in data else NoAction()
        decoders = set()
        for data_key in data:
            if data_key in Action.PKEYS:
                decoders.add(Action.PKEYS[data_key])
        for cls in sorted(decoders, key=lambda a: a.PROFILE_KEY_PRIORITY):
            a = cls.decode(data, a, self, 0)
        return a

    def restart(self, s: str | bytes) -> "ActionParser":
        if type(s) is bytes:
            s = s.decode("utf-8")
        try:
            self.tokens = [ActionParser.Token(token_type, string)
                           for token_type, string, *_ in generate_tokens(iter([s]).__next__)
                           if token_type != TokenType.ENDMARKER]
        except TokenError:
            self.tokens = None
        self.index = 0
        return self

    def _next_token(self):
        if self.tokens is None:
            raise ParseError("Syntax error")
        rv = self.tokens[self.index]
        self.index += 1
        return rv

    def _peek_token(self):
        if self.tokens is None:
            raise ParseError("Syntax error")
        return self.tokens[self.index]

    def _tokens_left(self):
        return self.tokens is not None and self.index < len(self.tokens)

    def _parse_parameter(self):
        t = self._next_token()
        while t.type in (TokenType.NL, TokenType.NEWLINE) or t.value == "\n":
            if not self._tokens_left():
                raise ParseError("Expected parameter at end of string")
            t = self._next_token()
        if t.type == TokenType.NAME:
            if self._tokens_left() and self._peek_token().type == TokenType.OP and self._peek_token().value == "(":
                self.index -= 1
                parameter = self._parse_action()
            elif (self._tokens_left() and t.value in Action.ALL and type(Action.ALL[t.value]) is dict
                  and self._peek_token().value == "."):
                self.index -= 1
                parameter = self._parse_action()
            else:
                if t.value not in ActionParser.CONSTS:
                    raise ParseError("Expected parameter, got '%s' which is not defined" % (t.value,))
                parameter = ActionParser.CONSTS[t.value]
            while self._tokens_left() and self._peek_token().type == TokenType.OP and self._peek_token().value == ".":
                self._next_token()
                if not self._tokens_left():
                    raise ParseError("Expected NAME after '.'")
                t = self._next_token()
                if not hasattr(parameter, t.value):
                    raise ParseError("%s has no attribute '%s'" % (parameter, t.value))
                parameter = getattr(parameter, t.value)
            if self._tokens_left() and self._peek_token().type == TokenType.OP and self._peek_token().value in RangeOP.OPS:
                op = self._next_token().value
                if parameter not in (STICK, SCButtons.LT, SCButtons.RT, SCButtons.X, SCButtons.Y):
                    raise ParseError("'%s' is not trigger nor axis" % (nameof(parameter),))
                if not self._tokens_left():
                    raise ParseError("Expected number after '%s'" % (op,))
                try:
                    number = float(self._next_token().value)
                except ValueError:
                    raise ParseError("Expected number after '%s'" % (op,))
                parameter = RangeOP(parameter, op, number)
            return parameter
        if t.type == TokenType.OP and t.value == "-":
            if not self._tokens_left() or self._peek_token().type != TokenType.NUMBER:
                raise ParseError("Expected number after '-'")
            return -self._parse_number()
        if t.type == TokenType.NUMBER:
            self.index -= 1
            return self._parse_number()
        if t.type == TokenType.STRING:
            return t.value[1:-1]
        raise ParseError("Expected parameter, got '%s'" % (t.value,))

    def _parse_number(self):
        t = self._next_token()
        if t.type != TokenType.NUMBER:
            raise ParseError("Expected number, got '%s'" % (t.value,))
        if "." in t.value or "e" in t.value.lower():
            return float(t.value)
        if t.value.lower().startswith("0x"):
            return int(t.value, 16)
        if t.value.lower().startswith("0b"):
            return int(t.value, 2)
        return int(t.value)

    def _parse_parameters(self):
        t = self._next_token()
        if t.type != TokenType.OP or t.value != "(":
            raise ParseError("Expected '(' of parameter list, got '%s'" % (t.value,))
        parameters = []
        while self._tokens_left():
            t = self._peek_token()
            if t.type == TokenType.OP and t.value == ")":
                self._next_token()
                return parameters
            parameters.append(self._parse_parameter())
            t = self._peek_token()
            while t.type in (TokenType.NL, TokenType.NEWLINE) or t.value == "\n":
                self._next_token()
                if not self._tokens_left():
                    raise ParseError("Expected ',' or end of parameter list after parameter '%s'" % (parameters[-1],))
                t = self._peek_token()
            if t.type == TokenType.OP and t.value == ")":
                pass
            elif t.type == TokenType.OP and t.value == ",":
                self._next_token()
            else:
                raise ParseError("Expected ',' or end of parameter list after parameter '%s'" % (parameters[-1],))
        raise ParseError("Unmatched parenthesis")

    def _create_action(self, cls, *pars):
        try:
            return cls(*pars)
        except ValueError as e:
            raise ParseError(str(e))
        except TypeError as e:
            print(e, file=sys.stderr)
            raise ParseError("Invalid number of parameters for '%s'" % (cls.COMMAND))

    def _parse_action(self, frm=None):
        if frm is None:
            frm = Action.ALL
        t = self._next_token()
        if t.type != TokenType.NAME:
            raise ParseError("Expected action name, got '%s'" % (t.value,))
        if t.value not in frm:
            raise ParseError("Unknown action '%s'" % (t.value,))
        action_name = t.value
        action_class = frm[action_name]
        if not self._tokens_left():
            return self._create_action(action_class)
        t = self._peek_token()
        parameters = []
        if t.type == TokenType.OP and t.value == ".":
            if type(action_class) is dict:
                self._next_token()
                return self._parse_action(action_class)
            raise ParseError("Unexpected '.' after '%s'" % (action_name,))
        if t.type == TokenType.OP and t.value == "(":
            parameters = self._parse_parameters()
            if not self._tokens_left():
                return self._create_action(action_class, *parameters)
            t = self._peek_token()
        if t.type == TokenType.NAME and t.value == "and":
            self._next_token()
            if not self._tokens_left():
                raise ParseError("Expected action after 'and'")
            return MultiAction(self._create_action(action_class, *parameters), self._parse_action())
        if t.type in (TokenType.NL, TokenType.NEWLINE) or t.value == "\n":
            self._next_token()
            if not self._tokens_left():
                return self._create_action(action_class, *parameters)
            t = self._peek_token()
            if t.type == TokenType.OP and t.value in (")", ","):
                return self._create_action(action_class, *parameters)
            return MultiAction(self._create_action(action_class, *parameters), self._parse_action())
        if t.type == TokenType.OP and t.value == ";":
            self._next_token()
            while self._tokens_left() and self._peek_token().type in (TokenType.NL, TokenType.NEWLINE):
                self._next_token()
            if not self._tokens_left():
                return self._create_action(action_class, *parameters)
            return Macro(self._create_action(action_class, *parameters), self._parse_action())
        return self._create_action(action_class, *parameters)

    def parse(self):
        if self.tokens is None:
            raise ParseError("Syntax error")
        a = self._parse_action()
        if self._tokens_left():
            raise ParseError("Unexpected '%s'" % (self._next_token().value,))
        return a


class TalkingActionParser(ActionParser):
    """ActionParser that reports parse failures instead of raising them."""

    def restart(self, string: str):
        self.string = string
        return ActionParser.restart(self, string)

    def parse(self):
        try:
            return ActionParser.parse(self)
        except ParseError as e:
            print(f"Warning: Failed to parse '{self.string}':", e, file=sys.stderr)
            return None
