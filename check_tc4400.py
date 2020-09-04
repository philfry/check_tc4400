#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# check_tc4400 - checks tc4400 modem status
# author, (c): Philippe Kueck <projects at unixadm dot org>

from optparse import OptionParser, OptionGroup

import base64
import urllib.request
import lxml.html
import re
from math import log

class thresholds:
    # snr limits [warn, crit]
    _snr = {
        'qam4096': [44, 42],
        'qam2048': [41, 39],
        'qam1024': [38, 36],
        'qam256':  [32, 30],
        'qam64':   [26, 24]
    }

    # receive level ranges
    # [min crit, min warn, max warn, max crit]
    _rlvl = {
        'qam4096': [ -2,   0, 24.1, 26.1],
        'qam2048': [ -4,  -2, 22.1, 24.1],
        'qam1024': [ -6,  -4, 20.1, 22.1],
        'qam256':  [ -8,  -6, 18.1, 20.1],
        'qam64':   [-14, -12, 12.1, 14.1]
    }

    # transmission level ranges
    # min crit, min warn, max warn, max crit
    _tlvl = {
        'atdma': [ 35, 37, 51.1, 53.1], # docsis 3.0
        'ofdm':  [ 38, 40, 48.1, 50.1]  # docsis 3.1
    }

ofdm_profiles = ['qam256', 'qam1024', 'qam2048', 'qam4096']

def nagexit(exitc, statusline, perfdata = []):
    print("{0}: {1}|{2}".format(
        {0:'OK',1:'WARNING',2:'CRITICAL',3:'UNKNOWN'}[exitc],
        "\n".join(statusline),
        " ".join(perfdata)
    ))
    exit(exitc)

def check(val, warn, crit):
    if warn <= crit <= val or val <= crit <= warn: return 2
    if warn <= val <= crit or crit <= val <= warn: return 1
    return 0

def check_range(val, critlo, warnlo, warnhi, crithi):
    if warnlo < val < warnhi: return 0
    if critlo < val <= warnlo or warnhi <= val < crithi: return 1
    return 2

def parse_table(table):
    head = []
    data = []
    for row in table.iter("tr"):
        cols = row.findall("td")
        if len(cols) == 0: continue
        if len(head) == 0:
            head = [i.text_content() for i in cols]
            continue
        tmp = [i.text_content() for i in cols]
        data.append(dict(zip(head, tmp)))
    return data

def get_dataset(_dict, key, value):
    for i in _dict:
        if key in i.keys() and i[key] == value:
            return i

def main():

    if options.file != None:
        try:
            with open(options.file, "r") as fh:
                data = fh.read()
        except (FileNotFoundError, PermissionError):
            nagexit(3, ["Cannot open file {}".format(options.file)])
    else:
        if options.startle:
            try: urllib.request.urlopen("http://"+options.host+"/cmconnectionstatus.html")
            except: pass
        try:
            req = urllib.request.Request(
                "http://"+options.host+"/cmconnectionstatus.html",
                headers = {'User-Agent': 'nagios/check_tc4400'}
            )
            if options.password != None:
                auth = base64.b64encode(
                    bytes("%s:%s" % (options.user, options.password), 'ascii')
                )
                req.add_header("Authorization", "Basic %s" % auth.decode('utf-8'))

            with urllib.request.urlopen(req, None, 60) as fh:
                data = fh.read()

        except urllib.error.URLError as e:
            nagexit(3, ["Connecting to webinterface failed with '{}'".format(e.reason)])

        except:
            import sys
            e = sys.exc_info()[0]
            nagexit(3, ["Something went horribly wrong: {}".format(e)])

    doc = lxml.html.document_fromstring(data)

    tables = doc.xpath('//table')
    if len(tables) == 0:
        nagexit(3, ["Unable to parse connectionstatus page"])

    floaty = re.compile(r'^-?\d+(\.\d+)?')

    perfdata = []
    statusline = []
    rc = 0

    # startup procedure
    startup_proc_data = parse_table(tables[0])

    for test in ["Connectivity State", "Boot State", "Configuration File"]:
        ds = get_dataset(startup_proc_data, "Procedure", test)
        if test == "Configuration File":
            statusline.append("using config file {}".format( ds["Comment"]))
        if ds["Status"] != "OK":
            rc = 2
            statusline.append("{} is {}".format(test, ds["Status"]))

    ds = get_dataset(startup_proc_data, "Procedure", "Security")
    if ds["Status"] != "Enabled":
        rc = 2
        statusline.append("Security is {}".format(ds["Status"]))

    # downstream channel status
    downstream_chan_data = parse_table(tables[1])
    for ds in downstream_chan_data:
        # output changed somewhen between SR70.12.33 and SR70.12.42
        try: rlvl = float(re.search(floaty, ds["Receive Level"]).group(0))
        except KeyError: rlvl = float(re.search(floaty, ds["Received Level"]).group(0))
        snr = float(re.search(floaty, ds["SNR/MER Threshold Value"]).group(0))
        frq = float(re.search(floaty, ds["Center Frequency"]).group(0))/10**6
        # output changed somewhen between SR70.12.33 and SR70.12.42
        if re.match(r'^OFDM(?: Downstream)?$', ds["Channel Type"]):
            # check lowest possible profile
            modulation = ofdm_profiles[int(ds["Modulation/Profile ID"].split(",")[0])]
            spec = "docsis31"
        else:
            modulation = ds["Modulation/Profile ID"].lower()
            spec = "docsis30"

        bits = int(log(int(re.search(r'(\d+)$', modulation).group(0)))/log(2))
        perfdata.append(
            'dn{c:02d}_snr={:.1f};;; dn{c:02d}_rlvl={:.1f};;; dn{c:02d}_cwpass={}c;;; dn{c:02d}_cwcorr={}c;;; dn{c:02d}_cwfail={}c;;; dn{c:02d}_bits={};;;'.format(
            snr, rlvl, ds["Unerrored Codewords"], ds["Corrected Codewords"], ds["Uncorrectable Codewords"], bits, c=int(ds["Channel Index"]),
        ))

        if ds["Lock Status"] != "Locked":
            if rc < 1: rc = 1
            statusline.append("uch{:02d}@{:.1f}MHz is {}".format(
                int(ds["Channel Index"]), frq, ds["Lock Status"]
            ))

        if ds["Bonding Status"] != "Bonded":
            if rc < 1: rc = 1
            statusline.append("uch{:02d}@{:.1f}MHz is {}".format(
                int(ds["Channel Index"]), frq, ds["Lock Status"]
            ))

        if spec == options.igndocsis: continue

        t_rc = check_range(rlvl, *thresholds._rlvl[modulation])
        if t_rc > 0:
            if rc < t_rc: rc = t_rc
            statusline.append("dch{:02d}@{:.1f}MHz signal out of range ({})".format(
                int(ds["Channel Index"]), frq, ds["Receive Level"]
            ))

        t_rc = check(snr, *thresholds._snr[modulation])
        if t_rc > 0:
            if rc < t_rc: rc = t_rc
            statusline.append("dch{:02d}@{:.1f}MHz SNR out of range ({})".format(
                int(ds["Channel Index"]), frq, ds["SNR/MER Threshold Value"]
            ))

    # upstream channel status
    upstream_chan_data = parse_table(tables[2])
    for ds in upstream_chan_data:
        tlvl = float(re.search(floaty, ds["Transmit Level"]).group(0))
        frq = float(re.search(floaty, ds["Center Frequency"]).group(0))/10**6
        modulation = ds["Modulation/Profile ID"].lower()

        perfdata.append(
            'up{c:02d}_tlvl={:.1f};;;'.format(tlvl, c=int(ds["Channel Index"]))
        )

        if ds["Lock Status"] != "Locked":
            if rc < 1: rc = 1
            statusline.append("uch{:02d}@{:.1f}MHz is {}".format(
                int(ds["Channel Index"]), frq, ds["Lock Status"]
            ))

        if ds["Bonding Status"] != "Bonded":
            if rc < 1: rc = 1
            statusline.append("uch{:02d}@{:.1f}MHz is {}".format(
                int(ds["Channel Index"]), frq, ds["Lock Status"]
            ))

        t_rc = check_range(tlvl, *thresholds._tlvl[modulation])
        if t_rc > 0:
            if rc < t_rc: rc = t_rc
            statusline.append("uch{:02d}@{:.1f}MHz signal out of range ({})".format(
                int(ds["Channel Index"]), frq, ds["Transmit Level"]
            ))


    # extra data
    extra_data = parse_table(tables[3])

    nagexit(rc, statusline, perfdata)



if __name__ == "__main__":
    desc = "%prog checks your tc4400's status and performance data."
    parser = OptionParser(description=desc,version="%prog version 0.8")
    gen_opts = OptionGroup(parser, "Generic options")
    thres_opts = OptionGroup(parser, "Threshold options")
    workaround_opts = OptionGroup(parser, "Workaround options")
    parser.add_option_group(gen_opts)
    parser.add_option_group(thres_opts)
    parser.add_option_group(workaround_opts)

    # -H / --host
    gen_opts.add_option("-H", "--hostname", dest="host",
        type="string", action="store", default="192.168.100.1",
        help="Hostname or ip address of your tc4400 modem.")

    # -u / --username
    gen_opts.add_option("-u", "--username", dest="user",
        type="string", action="store", default="admin",
        help="Username to authenticate with to the modem's webinterface.")

    # -p / --password
    gen_opts.add_option("-p", "--password", dest="password",
        type="string", action="store",
        help="Password to authenticate with to the modem's webinterface.")

    # -r / --read
    gen_opts.add_option("-r", "--read", dest="file",
        type="string", action="store",
        help="Read data from file (usually for debugging purposes)")

    # -i / --ignore
    thres_opts.add_option("-i", "--ignore", dest="igndocsis",
        type="string", action="store",
        help="""Do not check thresholds for DOCSISVER ("docsis30" or
"docsis31"). Collect perfdata though.
Useful when your line performance is really bad but your modem works
nonetheless, or you're connected both with docsis 3.0 and 3.1 but the modem
only uses either of them.""")

    # -s / --startle
    workaround_opts.add_option("-s", "--startle", dest="startle",
        action="store_true", default=False,
        help="Startle modem by sending an additional unauthorized dummy request")

    (options, args) = parser.parse_args()

    main()
