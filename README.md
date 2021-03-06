## NAME

```
check_tc4400
```

## SYNOPSIS

    check_tc4400 <OPTIONS>

## OPTIONS

- **H**,**hostname** _HOSTNAME_

    Hostname or ip address of your tc4400 modem.

- **u**,**username** _username_

    Username to authenticate with to the modem's webinterface.

- **p**,**password** _password_

    Password to authenticate with to the modem's webinterface.

- **r**,**read** _filename_

    Read data from file (usually for debugging purposes).

- **i**,**ignore** _{docsis30|docsis31}_

    Do not check thresholds for _{docsis30|docsis31}_. Collect perfdata though.
    Useful when your line performance is really bad but your modem works
    nonetheless, or you're connected both with docsis 3.0 and 3.1 but the modem
    only uses either of them.

- **s**,**startle**

    Startle the modem by sending an unauthorized dummy request prior to the
	"real" request for data. Use this workaround if your modem randomly times
	out with check_tc4400.

## DESCRIPTION

This script connects to the TC4400 webinterface and parses the connection status page.

It warns or returns a critical state if:

    - Connectivity State is not "OK"
    - Boot State is not "OK"
    - Configuration File is not "OK"
    - Security is not "Enabled"
    - downstream channel is not "Locked"
    - downstream channel signal/noise ratio is below a predefined value
    - downstream channel transmission level is odd
    - upstream channel transmission level is odd

see [20180617\_Pegelwerte.pdf](https://raw.githubusercontent.com/philfry/check_tc4400/master/20180617_Pegelwerte.pdf) for thresholds.

## AUTHOR

Philippe Kueck &lt;projects at unixadm dot org>

## EXAMPLE

![screenshot](https://raw.githubusercontent.com/philfry/check_tc4400/master/modemdata.png)
