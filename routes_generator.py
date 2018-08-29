#!/bin/python3
import sys
import re
import traceback

# HTTP/1.1 methods as seen in https://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html
HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'TRACE', 'CONNECT']

def print_usage():
    print ('usage:   ./routes_generator.py <input_file>')

multi_line_comment = False
alternative_return_function = 'jsonify'
decorate_all = False
decorator = ''

if len(sys.argv) != 2:
    print_usage()
    exit()

with open(sys.argv[1], 'r') as f:
    lines = f.readlines()

print ('\n')
for line in map(lambda x: x.strip(), lines):
    alternative_return = False
    try:
        if len(line) < 1:
            continue

        if line[0] is '#':
            print (line)
            continue

        if line[0] is '@':
            tmp2 = line.split(' ')
            if len(tmp2) < 2:
                print (line)
            else:
                if tmp2[1] == 'all':
                    decorate_all = True
                    decorator = tmp2[0]
                if tmp2[1] == 'none':
                    decorate_all = False
                    print (line)
            continue

        if line[0:3] == '\'\'\'':
            multi_line_comment = not multi_line_comment
            print (line)
            continue

        if multi_line_comment:
            print (line)
            continue

        tmp     = line.split(' ')
        route   = tmp[0]

        if len(tmp) > 1 and tmp[-1].upper() not in HTTP_METHODS:
            alternative_return = True
            alternative_return_function = tmp[-1]
            tmp = tmp[:-1]

        methods = [x.upper() for x in tmp[1:]]

        for method in methods:
            if method not in HTTP_METHODS:
                raise Exception(method+' is not a valid method')

        function_name  = '_'.join(x for x in methods) + '_'
        function_name += '_'.join(x for x in route.split('/') if '<' not in x)
        function_name  = function_name.lower()

        args = []
        arg = re.search(r'<.*>', route)
        if arg is not None:
            arg = arg.group()
            args.append(arg.replace('<', '').replace('>', ''))

        template_name = route

        if decorate_all:
            print (decorator)

        print ('@app.route(\'/{}\', methods={})'.format(route, [x for x in methods]))
        print ('def {}({}):'.format( function_name, ', '.join(x for x in args) ) )

        if alternative_return:
            print ('    return render_template(\'{}.html\')\n'.format(template_name))
        else:
            print ('    data = request.get_json()')
            print ('    return {}(data)\n'.format(alternative_return_function))

    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        print ('I don\'t like this line', line, file=sys.stderr)
