## NAME

check\_tc4400

## VERSION

0.1

## SYNOPSIS

```
check_tc4400 -H HOST -u USER -p PASS
```

## OPTIONS

- **H** _HOSTNAME_

    Hostname or ip address of your tc4400 modem.

- **u** _username_

    Username to authenticate with to the modem's webinterface.

- **p** _password_

    Password to authenticate with to the modem's webinterface.

## DESCRIPTION

This script connects to the TC4400 webinterface and parses the connection status page.

It warns or returns a critical state if:

```
* Connectivity State is not "OK"
* Boot State is not "OK"
* Configuration File is not "OK"
* Security is not "Enabled"
* downstream channel is not "Locked"
* downstream channel signal/noise ratio is below 32dB/30dB (QAM256)
* downstream channel signal/noise ratio is below 24dB/26dB (QAM64)
* downstream channel receive level is below -8dBmV/-6dBmV or above 18.1dBmV/20.1dBmV
* upstream channel transmission level is below 32dBmV/34dBmV or above 54.1dBmV/56.1dBmV
```

## DEPENDENCIES

- `LWP::UserAgent`
- `HTML::TableExtract`
- `Pod::Usage`
- `Getopt::Long`

## AUTHOR

Philippe Kueck &lt;projects at unixadm dot org>

## EXAMPLE

![screenshot](https://raw.githubusercontent.com/philfry/check_tc4400/master/modemdata.png)
