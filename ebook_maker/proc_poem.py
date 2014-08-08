#!/usr/bin/env python

from numpy import *
from os import system
from ebooklib.epub import *

import re
import sys
import pdb

############################################################

class poem:
    begin_sent  = re.compile( r'^[^a-z]*[A-Z]' );
    inline_sent = re.compile( r'\..*[ ]*[A-Z]' );

    @staticmethod
    def is_new_sent_head( line ):
        return poem.begin_sent.search( line )  != None;
    #

    @staticmethod
    def is_new_sent_in_line( line ):
        return poem.inline_sent.search( line ) != None;
    #

    @staticmethod
    def html_line( line, pads ):
        res = '<tr> <td>' +                               \
              '<div style=\"margin-left:%gem\">' % pads + \
              line + '</div>' +                           \
              '</td> <tr>';
        return res;
    #

    @staticmethod
    def set_ebook_handler( book ):
        poem.book       = book;
        poem.book.toc   = [  ];
        poem.book.spine = [ 'nav' ];
    #

    def __init__( self ):
        self.title        = '';
        self.content      = [  ];
        self.content_html = '<html> <body> CONT ' + \
                            ' </body> </html>';
        return;
    #

    def post_proc( self ):
        self.file_name = self.title.replace( ' ', '_' ) + \
                         '.xhtml';
        title_html     = '<h2>' + self.title + '</h2>';
        body_html      = '<table border=\"0\"> ';

        lines_in_sentence = 0;
        is_new_sect = False;
        for i, line in enumerate( self.content ):
            if poem.is_new_sent_head( line ) or \
               is_new_sect:
                pads = 0;
                lines_in_sentence = 0;
            else:
                if poem.is_new_sent_in_line( line ):
                    pads = 1
                    lines_in_sentence = 0;
                else:
                    pads = 2 + lines_in_sentence % 2;
                    lines_in_sentence += 1;
                #
            #

            if '__NEW_SECT__' in line:
                line = '&nbsp;';
                is_new_sect = True;
            else:
                is_new_sect = False;
            #
            
            body_html += poem.html_line( line, pads );
        #
        body_html += '</table>'
        content = title_html + body_html;
        self.content_html \
            = self.content_html.replace( 'CONT', content );
        return;
    #

    def write_to_epub( self ):
        c = EpubHtml( title     = self.title,     \
                      file_name = self.file_name, \
                      lang      = 'en'            );
        c.content = self.content_html;
        poem.book.add_item    ( c );
        poem.book.toc.append  ( c );
        poem.book.spine.append( c );
        return;
    #
#

def poem_parse( input_file ):
    result   = [  ];
    end_flag = 'Elizabeth Bishop';

    is_poem_start = True;
    with open( input_file, 'r' ) as f:
        for line in f:
            line = line.strip(  );
            if line == '':
                line = '__NEW_SECT__';
            #
            if is_poem_start:
                this_poem       = poem(  );
                this_poem.title = line;
                is_poem_start   = False;
            elif 'Elizabeth Bishop' in line:
                is_poem_start = True;
                this_poem.post_proc(  );
                result.append( this_poem );
            else:
                this_poem.content.append( line );
            #
        #
    #
    return result;
#

def create_poem_epub( author, title, input_file ):
    book = EpubBook(  );

    book.set_identifier( 'poem_test' );
    book.set_title( title );
    book.set_language( 'en' );
    book.add_author( author );

    poem.set_ebook_handler( book );
    poems = poem_parse( input_file );
    for p in poems:
        p.post_proc    (  );
        p.write_to_epub(  );
    #

    book.add_item( EpubNcx(  ) );
    book.add_item( EpubNav(  ) );

    style = '''
    @namespace epub "http://www.idpf.org/2007/ops";
    body
    {
    font-family: Cambria, Liberation Serif,\
    Bitstream Vera Serif, Georgia, Times,\
    Times New Roman, serif;
    }
    h2
    {
    text-align: left;
    text-transform: uppercase;
    font-weight: 200;
    }
    ol
    {
    list-style-type: none;
    }
    ol > li:first-child
    {
    margin-top: 0.3em;
    }
    nav[epub|type~='toc'] > ol > li > ol
    {
    list-style-type:square;
    }
    nav[epub|type~='toc'] > ol > li > ol > li
    {
    margin-top: 0.3em;
    }
    '''
    
    nav_css = EpubItem( uid        = "style_nav",     \
                        file_name  = "style/nav.css", \
                        media_type = "text/css",      \
                        content    = style            );
    book.add_item( nav_css )

    save_name = title.replace( ' ', '_' ) + '.epub';
    write_epub( save_name, book, {  } );
    return;
#

if __name__=='__main__':
    title      = 'Elizabeth Bishop: Collections';
    author     = 'Elizabeth Bishop';
    input_file = 'test_in.txt';

    create_poem_epub( author, title, input_file );
#
