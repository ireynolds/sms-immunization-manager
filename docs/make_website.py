'''
Copies the input directory recursively to the output and then converts every 
modified markdown file in the output to a corresponding HTML file.
'''

import argparse
import shutil
import os
import sys
import string
import markdown

args = None

# All of these options are required at the head of a markdown file,
# in the form "title: The Title Of This Page", and so on.
REQUIRED_OPTIONS = ['title', 'styles', 'home']

# The output is generated using the following template. There is one
# identifier for each REQUIRED_OPTION, plus one for the content
# in the body.
TEMPLATE = \
'''
<html>
    <head>
        <title>${__TITLE__}</title> 
        <link rel="stylesheet" type="text/css" href="${__STYLES__}">
    </head>
    </body>
        <br />
        <p><a href="${__HOME__}">Home</a></p>

        ${__BODY__}
    </body>
</html>
'''

def copy_to_output():
    '''Copies the markdown files into a new directory in which to create the HTML content.'''
    shutil.copytree(args.input, args.output)

def md_to_html():
    '''
    Convert each markdown file in the output directory to a corresponding HTML file, using
    the template above.
    '''
    for md_path, html_path in _md_html_paths():
        if os.path.exists(html_path):
            print "ERROR: Cannot have sources at both %s and %s (pick one)." % (md_path, html_path)
        _to_html(md_path, html_path)
        os.remove(md_path)

def _md_html_paths():
    '''
    Generates (md_path, html_path), where md_path is the path to a markdown file and html_path
    is the path to the corresponding HTML file, for each markdown file in the output directory.
    '''
    for dirpath, cdirnames, cfilenames in os.walk(args.output):
        for cfilename in cfilenames:
            if cfilename.endswith(".md"):
                name = cfilename[:-3]
                path = os.path.join(dirpath, name) 
                yield path + ".md", path + ".html"

def _to_html(md_path, html_path):
    '''Converts the given markdown file to a HTML file with the given path.'''
    if not html_path.startswith(args.output):
        print "ERROR: Programmer error: not writing to output directory."
        sys.exit(1) 

    with open(md_path, 'r') as input_file:
        meta, md = _read_meta(input_file)

    body = markdown.markdown(md)
    html = _apply_template(meta, body)

    with open(html_path, 'w') as output_file:
        output_file.write(html)

def _read_meta(input_file):
    '''Reads the metadata (in REQUIRED_OPTIONS) out of the head of the markdown file.'''
    meta = {}

    for _ in range(len(REQUIRED_OPTIONS)):
        line = input_file.readline().strip()
        sep = line.find(':')
        try:
            option, value = line[:sep].lower().strip(), line[sep + 1:].strip()
            if option not in REQUIRED_OPTIONS:
                raise  Exception()
            meta[option] = value
        except:
            print "ERROR: All .md files must start with '____: _____' for %s." % (REQUIRED_OPTIONS,)
            sys.exit(1)

    if len(meta) != len(REQUIRED_OPTIONS):
        print "You did not specify options %s" % (set(REQUIRED_OPTIONS) - set(meta.keys()),)

    return meta, input_file.read()

def _apply_template(meta, body):
    '''Given the metadata and HTML body, returns the complete HTML file.'''
    t = string.Template(TEMPLATE)
    return t.substitute({
        '__TITLE__': meta['title'],
        '__BODY__': body,
        '__STYLES__': meta['styles'],
        '__HOME__': meta['home']
    })

def main():
    copy_to_output()
    md_to_html()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    main()