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
    'atdma': [ 38, 40, 48.1, 50.1], # docsis 3.0
    'ofdm':  [ 35, 37, 51.1, 53.1]  # docsis 3.1
}
