#!/usr/bin/env python3
"""
VDF file reader
Copyright (C) 2017 Kozec

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as published by
the Free Software Foundation
"""
import shlex


def parse_vdf(fileobj):
	"""Converts VDF file or file-like object into python dict."""
	rv = {}
	stack = [rv]
	lexer = shlex.shlex(fileobj)
	key = None
	t = lexer.get_token()
	while t:
		if t == "{":
			if key is None:
				raise ValueError("Dict without key")
			value = {}
			if key in stack[-1]:
				lst = ensure_list(stack[-1][key])
				lst.append(value)
				stack[-1][key] = lst
			else:
				stack[-1][key] = value
			stack.append(value)
			key = None
		elif t == "}":
			if len(stack) < 2:
				raise ValueError("'}' without '{'")
			stack = stack[0:-1]
		elif key is None:
			key = t.strip('"').lower()
		elif key in stack[-1]:
			lst = ensure_list(stack[-1][key])
			lst.append(t.strip('"'))
			stack[-1][key] = lst
			key = None
		else:
			stack[-1][key] = t.strip('"')
			key = None
		t = lexer.get_token()
	if len(stack) > 1:
		raise ValueError("'{' without '}'")
	return rv


def ensure_list(value):
	return value if type(value) == list else [value]


if __name__ == "__main__":
	with open('app_generic.vdf', "r") as fileobj:
		print(parse_vdf(fileobj))
