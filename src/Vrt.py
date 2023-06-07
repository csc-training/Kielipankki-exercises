import datetime
import re
import logging

def _is_comment(s): return s.startswith('<!--') and s.endswith('-->')

def _is_buggy_comment(s):
    return s.startswith('<--') and s.endswith('-->')

def _is_opening_tag(s):
    return s.startswith('<') and (not s.startswith('</')) and s.endswith('>')

def _is_closing_tag(s):
    return s.startswith('</') and s.endswith('>')

#attribs_re = re.compile(r'[^ ="]+="(?:[^"]|(?:\"))+"')
_attribs_re = re.compile(r'[^ ="]+="[^"]+"')
def _get_tag_name_and_attribs(tag):
    tag = tag[1:-1] # strip <>
    if ' ' not in tag:
        return (tag, {}) # Just a tag name
    name = tag[:tag.index(" ")]
    tag = tag[tag.index(" ") + 1:] # remove name part, the rest is an attrib list
    attribs = {}
    for attr_val in re.findall(_attribs_re, tag):
        equals_index = attr_val.index('=')
        attribute = attr_val[:equals_index]
        attribs[attribute] = attr_val[equals_index+1:].strip('"')
    return (name, attribs)

class VrtReader:
    
    class VrtText:
        
        def __init__(self, attribs):
            self.attribs = attribs
            try:
                self.date = datetime.datetime.strptime(self.attribs["datefrom"], "%Y%m%d").date()
            except:
                logging.warning("Failed to parse datefrom field!")
            self.sentences = []
            
        def tokens(self):
            retval = []
            for sentence in self.sentences:
                retval += sentence.tokens
            return retval
        
    class VrtSentence:
        def __init__(self, attribs):
            self.attribs = attribs
            self.tokens = []
            
    def __init__(self, fobj_or_filename):
        if type(fobj_or_filename) == str:
            fobj = open(fobj_or_filename)
        else:
            fobj = fobj_or_filename
        firstline = fobj.readline().strip()
        if not (_is_comment(firstline) or _is_buggy_comment(firstline)) \
           or ':' not in firstline:
            raise Exception(
                "Couldn't find positional argument comment in first line")
        positional_args_start = firstline.index(':') + 1
        positional_args_stop = firstline.rindex('-->')
        self.token_fields = firstline[positional_args_start:positional_args_stop].strip().split()
        self.texts = [] # this will contain sublists of attribs and children
        for i, line in enumerate(fobj):
            line = line.strip()
            if _is_closing_tag(line) or _is_comment(line) or line == '':
                continue # We ignore complicated XML possibilities
            elif _is_opening_tag(line):
                name, attribs = _get_tag_name_and_attribs(line)
                if name == "text":
                    self.texts.append(self.VrtText(attribs))
                elif name == "sentence":
                    self.texts[-1].sentences.append(self.VrtSentence(attribs))
                else:
                    logging.warning(f"Ignored <{name}> element on line {i+1} - we only handle text and sentence elements!")
            else: # Should be a token
                self.texts[-1].sentences[-1].tokens.append(line.split('\t'))

    def info(self):
        text_attribs = set()
        sentence_attribs = set()
        n_texts = len(self.texts)
        n_sentences = n_tokens = 0
        for text in self.texts:
            text_attribs.update(text.attribs.keys())
            n_sentences += len(text.sentences)
            for sentence in text.sentences:
                sentence_attribs.update(sentence.attribs.keys())
                n_tokens += len(sentence.tokens)
        text_attribs_txt = '\n'.join([f"    {key}" for key in text_attribs])
        sentence_attribs_txt = '\n'.join([f"    {key}" for key in sentence_attribs])
        token_fields_txt = '\n'.join([f"    {field}" for field in self.token_fields])

        return f'''
Document contains
    {n_texts:,} texts
    {n_sentences:,} sentences
    {n_tokens:,} tokens
Text attributes are
{text_attribs_txt}
Sentence attributes are
{sentence_attribs_txt}
Token fields are
{token_fields_txt}
'''

    def token_values(self, field):
        values = set()
        if field not in self.token_fields:
            raise ValueError(f"Requested field {field} not present. Available fields are {self.token_fields}")
        idx = self.token_fields.index(field)
        for text in self.texts:
            for sentence in text.sentences:
                for token in sentence.tokens:
                    values.update(token[idx].split('|'))
        return list(values)

    def map_tokens_to_field(self, tokens, field):
        if field not in self.token_fields:
            raise ValueError(f"Requested field {field} not present. Available fields are {self.token_fields}")
        idx = self.token_fields.index(field)
        return [token[idx] for token in tokens]

    def token_field_is_value(self, token, field, value):
        if field not in self.token_fields:
            raise ValueError(f"Requested field {field} not present. Available fields are {self.token_fields}")
        idx = self.token_fields.index(field)
        return token[idx] == value


if __name__ == '__main__':
    import sys
    print(parse_file(open(sys.argv[1])))
