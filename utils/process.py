"""
Cuckoo Sandbox - Automated Malware Analysis
Copyright (C) 2010-2014 Cuckoo Foundation

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import copy
import docutils.nodes
import docutils.utils
import docutils.parsers.rst
import jinja2
import json
import os.path
import sys


class DefitionProcessor(object):
    def __init__(self, data_dir, out_dir, sigs):
        self.data_dir = data_dir

        fs_loader = jinja2.FileSystemLoader(data_dir)
        self.templ_env = jinja2.Environment(loader=fs_loader)

        base_sigs_path = os.path.join(data_dir, 'base_sigs.json')
        types_path = os.path.join(data_dir, 'types.conf')
        is_success_path = os.path.join(data_dir, 'is-success.conf')

        self.hooks_c = os.path.join(out_dir, 'hooks.c')
        self.hooks_h = os.path.join(out_dir, 'hooks.h')

        self.sigs = sigs

        self.types = {}
        for line in open(types_path, 'rb'):
            key, value = line.split('=', 1)
            self.types[key.strip()] = value.strip()

        self.is_success = {}
        for line in open(is_success_path, 'rb'):
            key, value = line.split('=', 1)
            self.is_success[key.strip()] = value.strip()

        self.sigcnt, self.base_sigs = 0, []

        for entry in json.load(open(base_sigs_path, 'rb')):
            entry['index'] = self.sigcnt
            for param in entry['parameters']:
                param['alias'] = param['argname']
                param['log'] = True

            self.base_sigs.append(entry)
            self.sigcnt += 1

    def parser_settings(self):
        components = docutils.parsers.rst.Parser,
        settings = docutils.frontend.OptionParser(components=components)
        return settings.get_default_values()

    def read_document(self, sig):
        doc = docutils.utils.new_document(os.path.basename(sig),
                                          self.parser_settings())
        parser = docutils.parsers.rst.Parser()
        parser.parse(open(sig, 'rb').read(), doc)
        return parser

    def template(self, name):
        return self.templ_env.get_template('%s.jinja2' % name)

    def _parse_signature(self, text):
        ret = {}
        for line in text.split('\n'):
            if not line.startswith('*'):
                raise Exception('Every line of the signature should start '
                                'with an asterisks: %r.' % line)

            key, value = line[1:].split(':', 1)
            ret[key.strip().lower().replace(' ', '_')] = value.strip()

        return ret

    def _parse_parameters(self, text):
        ret = []
        for line in text.split('\n'):
            if not line.startswith('*'):
                raise Exception('Parameter declaration should have at least '
                                'one asterisks: %r.' % line)

            line = line[1:].strip()

            # We have to log this argument.
            log = False
            if line.startswith('*'):
                log = True
                line = line[1:].strip()

            # Certain keywords are to be ignored.
            argtype = []
            while line.startswith(('const ', 'CONST ', 'struct ')):
                argtype.append(line.split(' ', 1)[0])
                line = line.split(' ', 1)[1].strip()

            if line.count(' ') == 1:
                argtype.append(line.split()[0])
                alias = argname = line.split()[1]
            elif line.count(' ') == 2:
                argtype.append(line.split()[0])
                argname, alias = line.split()[1:]
            else:
                raise Exception('Incorrect whitespace count in parameter '
                                'line: %r.' % line)

            alias = alias.replace('*', '').replace('[]', '').strip()

            if argname.startswith('*'):
                argname = argname[1:].strip()
                argtype.append('*')

            if argname.endswith('[]'):
                argname = argname[:-2].strip()
                if argtype[-1] == '*':
                    argtype[-1] += '*'
                else:
                    argtype.append('*')

            if argname.endswith(','):
                raise Exception('Parameter line ends with a comma: %s' % line)

            ret.append(dict(argtype=' '.join(argtype).strip(),
                            argname=argname.strip(),
                            alias=alias, log=log))
        return ret

    def _parse_pre(self, text):
        return text.split('\n')

    def _parse_prelog(self, text):
        return self._parse_logging(text)

    def _parse_ensure(self, text):
        ret = []
        for line in text.split('\n'):
            if line.startswith('*'):
                line = line[1:].strip()

            ret.append(line)
        return ret

    def _parse_post(self, text):
        return text.split('\n')

    def _parse_logging(self, text):
        ret = []
        for line in text.split('\n'):
            if line.startswith('*'):
                line = line[1:].strip()

            argtype, argname, argvalue = line.strip().split(' ', 2)
            ret.append(dict(argtype=argtype,
                            argname=argname,
                            argvalue=argvalue))
        return ret

    def _parse_paragraph(self, paragraph, literal_block):
        if not isinstance(paragraph, docutils.nodes.paragraph):
            raise Exception('Node must be a paragraph.')

        if not isinstance(literal_block, docutils.nodes.literal_block):
            raise Exception('Child node must be a literal block.')

        key = paragraph.astext().replace(':', '').lower()
        if not hasattr(self, '_parse_' + key):
            raise Exception('No parser known for the %r section.' % key)

        return key, getattr(self, '_parse_' + key)(literal_block.astext())

    def _prevent_overwrite(self, key, value, global_values):
        if key != 'signature' or key not in global_values:
            return

        prevents = dict(
            library='Library',
            calling_convention='Calling convention',
            category='Category',
            return_value='Return value',
        )

        for k, v in prevents.items():
            if k in global_values[key] and k in value:
                raise Exception('Please do not overwrite %r values.' % v)

    def normalize(self, doc):
        global_values, start = {}, 0

        while isinstance(doc.document.children[start],
                         docutils.nodes.paragraph):
            try:
                children = doc.document.children
                key, value = self._parse_paragraph(children[start],
                                                   children[start+1])
            except Exception as e:
                raise Exception('Error parsing global node: %s' % e.message)

            global_values[key] = value
            start += 2

        for entry in doc.document.ids.values():
            if not isinstance(entry.children[0], docutils.nodes.title):
                raise Exception('Node must be a title.')

            apiname = entry.children[0].astext()
            children = entry.children

            row = copy.deepcopy(global_values)

            row['apiname'] = apiname
            row['index'] = self.sigcnt
            self.sigcnt += 1

            for x in xrange(1, len(children), 2):
                try:
                    key, value = self._parse_paragraph(children[x],
                                                       children[x+1])

                    if key in row:
                        self._prevent_overwrite(key, value, global_values)
                        row[key].update(value)
                    else:
                        row[key] = value

                except Exception as e:
                    raise Exception('Error parsing node of api %r: %s' %
                                    (apiname, e.message))

            # If no is_success handler has been defined then use one based on
            # the return value. (This is the default behavior.)
            if 'is_success' not in row['signature']:
                retval = row['signature']['return_value']
                if retval not in self.is_success:
                    raise Exception('Unknown return_value %r for api %r.' %
                                    (retval, row['apiname']))

                row['signature']['is_success'] = self.is_success[retval]

            # Check the calling convention.
            if row['signature'].get('calling_convention') != 'WINAPI':
                raise Exception('Calling convention of %r must be WINAPI.' %
                                row['apiname'])

            self.explain.append(row)
            yield row

    def initial_header(self, f):
        print>>f, '#ifndef MONITOR_HOOKS_H'
        print>>f, '#define MONITOR_HOOKS_H'
        print>>f
        print>>f, '#include <winsock2.h>'
        print>>f, '#include <windows.h>'
        print>>f, '#include <wininet.h>'
        print>>f, '#include <windns.h>'
        print>>f, '#include <mswsock.h>'
        print>>f, '#include <tlhelp32.h>'
        print>>f, '#include "ntapi.h"'
        print>>f

    def ending_header(self, f):
        print>>f, '#endif'

    def initial_source(self, f):
        print>>f, '#include <stdio.h>'
        print>>f, '#include <stdint.h>'
        print>>f, '#include "%s"' % os.path.basename(self.hooks_h)
        print>>f, '#include "dropped.h"'
        print>>f, '#include "hooking.h"'
        print>>f, '#include "ntapi.h"'
        print>>f, '#include "log.h"'
        print>>f, '#include "misc.h"'
        print>>f, '#include "pipe.h"'
        print>>f, '#include "sleep.h"'

    def ending_source(self, f):
        pass

    def write(self, h, s, hook):
        for arg in hook.get('parameters', []):
            if arg['log'] and arg['argtype'] not in self.types:
                raise Exception('Unknown argtype %r.' % arg['argtype'])

        print>>h, self.template('header').render(hook=hook, types=self.types)
        print>>h

        print>>s, self.template('source').render(hook=hook, types=self.types)
        print>>s

    def process(self):
        h = open(self.hooks_h, 'wb')
        s = open(self.hooks_c, 'wb')

        self.initial_header(h)
        self.initial_source(s)

        self.explain = self.base_sigs

        for sig in self.sigs:
            for hook in self.normalize(self.read_document(sig)):
                self.write(h, s, hook)

        print>>s, self.template('explain').render(sigs=self.explain,
                                                  types=self.types)

        self.ending_header(h)
        self.ending_source(s)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: python %s <datadir> <outdir> <sigs.rst..>' % sys.argv[0]
        exit(1)

    dp = DefitionProcessor(sys.argv[1], sys.argv[2], sys.argv[3:])
    dp.process()