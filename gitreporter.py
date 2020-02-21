#!/usr/bin/env python3
#
# GitReporter
#   adam@msys.se 2015-2020
#
import os
import sys
import time
import smtplib
import re
import configparser
import ansiconv
from subprocess import run,PIPE
from platform import node
from email.mime.text import MIMEText
from datetime import date,datetime
from subprocess import check_output,call

# defs
SETTINGS = 'settings'
DIFF_LEN_REQUIRED = 10

#
# report
#
def report(cfg, contents):
    mb = "<html><head><title>%s</title>\n" % cfg.get(SETTINGS, 'mail_title')
    mb += "<style>body { font-family:Arial,sans-serif; } %s</style>\n" % ansiconv.base_css()
    mb += "</head></body>\n"
    mb += "<h1>%s</h1>\n" % cfg.get(SETTINGS, 'mail_title')
    mb += "<p>%s</p>\n" % cfg.get(SETTINGS, 'mail_ingress')
    mb += "<hr><p><pre>\n"
    mb += contents
    mb += "</pre></p><hr>\n"
    mb += "<p>This message was created by <b>GitReporter</b> on <b>%s</b> at %s</p>\n" % (node(), datetime.now())
    mb += "</body></html>\n"

    # create mime mail
    msg = MIMEText(mb, 'html')
    msg['Subject'] = cfg.get(SETTINGS, 'mail_subject')
    msg['From'] = cfg.get(SETTINGS, 'mail_from')
    msg['To'] = cfg.get(SETTINGS, 'mail_receptient')

    # save file as well
    if cfg.get(SETTINGS, 'mail_result_file'):
        with open(cfg.get(SETTINGS, 'mail_result_file'), 'w') as f:
            f.write(mb)
        print('*** report file written')

    # send mail or not
    if cfg.getboolean(SETTINGS, 'mail_enable'):
        # send mail
        s = smtplib.SMTP(cfg.get(SETTINGS, 'mail_smtp'))
        s.sendmail(msg['From'], [ msg['To'] ], msg.as_string())
        s.quit()
        print('*** email sent')



#
# main
#
def main(cfg):
    # get working directory
    wd = cfg.get(SETTINGS, 'repo_path')

    # perform git add
    cmd = cfg.get(SETTINGS, 'git_cmd_add').split(' ')
    p = run(cmd, cwd=wd, stdout=PIPE)
    print('*** git add done')

    # perform git diff
    cmd = cfg.get(SETTINGS, 'git_cmd_diff').split(' ')
    p = run(cmd, cwd=wd, stdout=PIPE)
    print('*** git diff done')
    diffo = p.stdout.decode('utf-8')

    # only commit and report if there is a diff output
    if len(diffo) < DIFF_LEN_REQUIRED:
        print('*** no changes detected, will stop here')
        return False
    else:
        print('*** changes detected (%d bytes), will proceed' % len(diffo)) 

    # perform git commit
    cmd = cfg.get(SETTINGS, 'git_cmd_commit').split(' ')
    p = run(cmd, cwd=wd, stdout=PIPE)
    print('*** commited')

    # perform redacting
    if cfg.getboolean(SETTINGS, 'redact_enable'):
        cre = re.compile(cfg.get(SETTINGS, 'redact_pattern'), flags=re.MULTILINE)
        replace = cfg.get(SETTINGS, 'redact_replace')
        print('*** perfoming redaction')
        diffr = re.sub(cre, replace, diffo)

    # remove diff and index lines
    if cfg.getboolean(SETTINGS, 'redact_minimize'):
        cre = re.compile(r'(diff\s--git\s.+\n|index\s.+\n|---\s.+\n)', flags=re.MULTILINE)
        diffr = re.sub(cre, '', diffr)

    # send report
    report(cfg, ansiconv.to_html(diffr))
    print('*** report done')



#
# main
#
if __name__ == "__main__":
    #  read configuration
    try:
        sys.argv[1]
        cfg = configparser.RawConfigParser()
        cfg.read(sys.argv[1])
    except IndexError:
        print("Fatal error! No configuration specified")
        sys.exit(1)
    except:
        print("Fatal error! Unable to parse configuration")
        sys.exit(1)

    # main
    main(cfg)

    # exit nicely
    sys.exit(0)

