<?php
/*
 *
 * pnp4nagios template for check_tc4400.
 *
 * use RRD_STORAGE_TYPE = MULTIPLE.
 *
 * Author: Philippe Kueck <projects at unixadm dot org>
 *
 */

$myds = array();
for ($i = 1; $i <= count($DS); $i++) {$myds[$NAME[$i]] = $i;}

// ==== upstream transmision level ====
$i++;
$ds_name[$i] = "us_tlvl";
$opt[$i] = " --vertical-label dBmV -E -b 1000 --title \"Upstream transmission level\" ";
$def[$i]  = rrd::line(1, "32", "#ff0000", ":dashes=5");
$def[$i] .= rrd::line(1, "34", "#e0e000", ":dashes=5");
$def[$i] .= rrd::line(1, "54.1", "#e0e000", ":dashes=5");
$def[$i] .= rrd::line(1, "56.1", "#ff0000", ":dashes=5");
for ($c = 1; $c <= 5; $c++) {
    $v = sprintf("up%02d_tlvl", $c);
    $def[$i] .= rrd::def($v, $RRDFILE[$myds[$v]], $DS[$myds[$v]], "AVERAGE");
    $def[$i] .= rrd::line1($v, rrd::color($c), rrd::cut("channel $c", 24));
    $def[$i] .= rrd::gprint($v, array("LAST", "AVERAGE", "MIN", "MAX"), "%3.1lf dBmV");
}

// ==== downstream SNR ====
$i = 0;
$ds_name[$i] = "ds_snr";
$opt[$i] = " --vertical-label dB -E -b 1000 --title \"Downstream SNR\" ";
// limits for QAM256
$def[$i] = rrd::hrule("32", "#e0e000", ":dashes=5");
$def[$i] .= rrd::hrule("30", "#ff0000", ":dashes=5");
for ($c = 1; $c <= 31; $c++) {
    $v = sprintf("dn%02d_snr", $c);
    $def[$i] .= rrd::def($v, $RRDFILE[$myds[$v]], $DS[$myds[$v]], "AVERAGE");
    $def[$i] .= rrd::line1($v, rrd::color($c), rrd::cut("channel $c", 24));
    $def[$i] .= rrd::gprint($v, array("LAST", "AVERAGE", "MIN"), "%3.1lf dB");
}

// ==== downstream receive level ====
$i++;
$ds_name[$i] = "ds_rlvl";
$opt[$i] = " --vertical-label dBmV -E -b 1000 --title \"Downstream receive level\" ";
$def[$i]  = rrd::line(1, "-8", "#ff0000", ":dashes=5");
$def[$i] .= rrd::line(1, "-6", "#e0e000", ":dashes=5");
$def[$i] .= rrd::line(1, "18.1", "#e0e000", ":dashes=5");
$def[$i] .= rrd::line(1, "20.1", "#ff0000", ":dashes=5");
for ($c = 1; $c <= 31; $c++) {
    $v = sprintf("dn%02d_rlvl", $c);
    $def[$i] .= rrd::def($v, $RRDFILE[$myds[$v]], $DS[$myds[$v]], "AVERAGE");
    $def[$i] .= rrd::line1($v, rrd::color($c), rrd::cut("channel $c", 24));
    $def[$i] .= rrd::gprint($v, array("LAST", "AVERAGE", "MIN", "MAX"), "%3.1lf dBmV");
}

// ==== downstream codewords ====
foreach (array(
    'cwpass' => 'unerrored',
    'cwcorr' => 'corrected',
    'cwfail' => 'uncorrectable'
) as $id => $title) {
    $i++;
    $ds_name[$i] = "ds_$id";
    $opt[$i] = " -E -b 1000 --title \"Downstream $title codewords\" ";
    $def[$i] = "";
    for ($c = 1; $c <= 31; $c++) {
    	$v = sprintf("dn%02d_%s", $c, $id);
    	$def[$i] .= rrd::def($v, $RRDFILE[$myds[$v]], $DS[$myds[$v]], "AVERAGE");
    	$def[$i] .= rrd::line1($v, rrd::color($c), rrd::cut("channel $c", 24));
    	$def[$i] .= rrd::gprint($v, array("LAST", "AVERAGE", "MAX"), "%7.0lf");
    }
}
