"""
pyrad.proc.process_retrieve
===========================

Functions for retrieving new moments and products

.. autosummary::
    :toctree: generated/

    process_signal_power
    process_rcs_pr
    process_rcs
    process_vol_refl
    process_snr
    process_l
    process_cdr
    process_rainrate
    process_bird_density


"""

from copy import deepcopy
from warnings import warn

import pyart

from ..io.io_aux import get_datatype_fields, get_fieldname_pyart


def process_signal_power(procstatus, dscfg, radar_list=None):
    """
    Computes the signal power in dBm

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : list of string. Dataset keyword
            The input data types
        mflossv : float. Global keyword
            The matching filter losses of the vertical channel. Used if input
            is vertical reflectivity
        radconstv : float. Global keyword
            The vertical channel radar constant. Used if input is vertical
            reflectivity
        lrxv : float. Global keyword
            The receiver losses from the antenna feed to the reference point.
            [dB] positive value
            Used if input is vertical reflectivity
        lradomev : float. Global keyword
            The 1-way dry radome losses [dB] positive value.
            Used if input is vertical reflectivity
        mflossh : float. Global keyword
            The matching filter losses of the vertical channel. Used if input
            is horizontal reflectivity
        radconsth : float. Global keyword
            The horizontal channel radar constant. Used if input is horizontal
            reflectivity
        lrxh : float. Global keyword
            The receiver losses from the antenna feed to the reference point.
            [dB] positive value
            Used if input is horizontal reflectivity
        lradomeh : float. Global keyword
            The 1-way dry radome losses [dB] positive value.
            Used if input is horizontal reflectivity
        attg : float. Dataset keyword
            The gas attenuation
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """

    if procstatus != 1:
        return None, None

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
        if datatype == 'dBZ':
            refl_field = 'reflectivity'
        if datatype == 'dBuZ':
            refl_field = 'unfiltered_reflectivity'
        if datatype == 'dBZc':
            refl_field = 'corrected_reflectivity'
        if datatype == 'dBuZc':
            refl_field = 'corrected_unfiltered_reflectivity'
        if datatype == 'dBZv':
            refl_field = 'reflectivity_vv'
        if datatype == 'dBuZv':
            refl_field = 'unfiltered_reflectivity_vv'
        if datatype == 'dBuZvc':
            refl_field = 'corrected_unfiltered_reflectivity_vv'

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    if refl_field not in radar.fields:
        warn('Unable to obtain signal power. Missing field '+refl_field)
        return None, None

    if refl_field.endswith('_vv'):
        pwr_field = 'signal_power_vv'

        lmf = dscfg.get('mflossv', None)
        radconst = dscfg.get('radconstv', None)
        lrx = dscfg.get('lrxv', 0.)
        lradome = dscfg.get('lradomev', 0.)
    else:
        pwr_field = 'signal_power_hh'

        lmf = dscfg.get('mflossh', None)
        radconst = dscfg.get('radconsth', None)
        lrx = dscfg.get('lrxh', 0.)
        lradome = dscfg.get('lradomeh', 0.)

    attg = dscfg.get('attg', None)

    s_pwr = pyart.retrieve.compute_signal_power(
        radar, lmf=lmf, attg=attg, radconst=radconst, lrx=lrx,
        lradome=lradome, refl_field=refl_field, pwr_field=pwr_field)

    # prepare for exit
    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()
    new_dataset['radar_out'].add_field(pwr_field, s_pwr)

    return new_dataset, ind_rad


def process_rcs_pr(procstatus, dscfg, radar_list=None):
    """
    Computes the radar cross-section (assuming a point target) from radar
    reflectivity by first computing the received power and then the RCS from
    it.

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : list of string. Dataset keyword
            The input data types
        antenna_gain : float. Global keyword
            The antenna gain [dB]
        txpwrv : float. Global keyword
            The transmitted power of the vertical channel [dBm]. Used if input
            is vertical reflectivity
        mflossv : float. Global keyword
            The matching filter losses of the vertical channel. Used if input
            is vertical reflectivity
        radconstv : float. Global keyword
            The vertical channel radar constant. Used if input is vertical
            reflectivity
        lrxv : float. Global keyword
            The receiver losses from the antenna feed to the reference point.
            [dB] positive value
            Used if input is vertical reflectivity
        ltxv : float. Global keyword
            The transmitter losses from the output of the high power amplifier
            to the antenna feed.
            [dB] positive value
            Used if input is vertical reflectivity
        lradomev : float. Global keyword
            The 1-way dry radome losses [dB] positive value.
            Used if input is vertical reflectivity
        txpwrh : float. Global keyword
            The transmitted power of the horizontal channel [dBm]. Used if input
            is horizontal reflectivity
        mflossh : float. Global keyword
            The matching filter losses of the vertical channel. Used if input
            is horizontal reflectivity
        radconsth : float. Global keyword
            The horizontal channel radar constant. Used if input is horizontal
            reflectivity
        lrxh : float. Global keyword
            The receiver losses from the antenna feed to the reference point.
            [dB] positive value
            Used if input is horizontal reflectivity
        ltxh : float. Global keyword
            The transmitter losses from the output of the high power amplifier
            to the antenna feed.
            [dB] positive value
            Used if input is horizontal reflectivity
        lradomeh : float. Global keyword
            The 1-way dry radome losses [dB] positive value.
            Used if input is horizontal reflectivity
        attg : float. Dataset keyword
            The gas attenuation
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """

    if procstatus != 1:
        return None, None

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
        if datatype == 'dBZ':
            refl_field = 'reflectivity'
        if datatype == 'dBuZ':
            refl_field = 'unfiltered_reflectivity'
        if datatype == 'dBZc':
            refl_field = 'corrected_reflectivity'
        if datatype == 'dBuZc':
            refl_field = 'corrected_unfiltered_reflectivity'
        if datatype == 'dBZv':
            refl_field = 'reflectivity_vv'
        if datatype == 'dBuZv':
            refl_field = 'unfiltered_reflectivity_vv'
        if datatype == 'dBuZvc':
            refl_field = 'corrected_unfiltered_reflectivity_vv'

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    if refl_field not in radar.fields:
        warn('Unable to obtain RCS. Missing field '+refl_field)
        return None, None

    if refl_field.endswith('_vv'):
        rcs_field = 'radar_cross_section_vv'

        lmf = dscfg.get('mflossv', None)
        radconst = dscfg.get('radconstv', None)
        lrx = dscfg.get('lrxv', 0.)
        ltx = dscfg.get('ltxv', 0.)
        lradome = dscfg.get('lradomev', 0.)
        tx_pwr = dscfg.get('txpwrv', None)
    else:
        rcs_field = 'radar_cross_section_hh'

        lmf = dscfg.get('mflossh', None)
        radconst = dscfg.get('radconsth', None)
        lrx = dscfg.get('lrxh', 0.)
        ltx = dscfg.get('ltxh', 0.)
        lradome = dscfg.get('lradomeh', 0.)
        tx_pwr = dscfg.get('txpwrh', None)

    antenna_gain = dscfg.get('AntennaGain', None)
    attg = dscfg.get('attg', None)

    rcs_dict = pyart.retrieve.compute_rcs_from_pr(
        radar, lmf=lmf, attg=attg, radconst=radconst, tx_pwr=tx_pwr,
        antenna_gain=antenna_gain, lrx=lrx, ltx=ltx,
        lradome=lradome, refl_field=refl_field, rcs_field=rcs_field)

    # prepare for exit
    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()
    new_dataset['radar_out'].add_field(rcs_field, rcs_dict)

    return new_dataset, ind_rad


def process_rcs(procstatus, dscfg, radar_list=None):
    """
    Computes the radar cross-section (assuming a point target) from radar
    reflectivity.

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : list of string. Dataset keyword
            The input data types
        kw2 : float. Dataset keyowrd
            The water constant
        pulse_width : float. Dataset keyowrd
            The pulse width [s]
        beamwidthv : float. Global keyword
            The vertical polarization antenna beamwidth [deg]. Used if input
            is vertical reflectivity
        beamwidthh : float. Global keyword
            The horizontal polarization antenna beamwidth [deg]. Used if input
            is horizontal reflectivity
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """

    if procstatus != 1:
        return None, None

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
        if datatype == 'dBZ':
            refl_field = 'reflectivity'
        if datatype == 'dBuZ':
            refl_field = 'unfiltered_reflectivity'
        if datatype == 'dBZc':
            refl_field = 'corrected_reflectivity'
        if datatype == 'dBuZc':
            refl_field = 'corrected_unfiltered_reflectivity'
        if datatype == 'dBZv':
            refl_field = 'reflectivity_vv'
        if datatype == 'dBuZv':
            refl_field = 'unfiltered_reflectivity_vv'
        if datatype == 'dBuZvc':
            refl_field = 'corrected_unfiltered_reflectivity_vv'

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    if refl_field not in radar.fields:
        warn('Unable to obtain RCS. Missing field '+refl_field)
        return None, None

    if refl_field.endswith('_vv'):
        rcs_field = 'radar_cross_section_vv'

        beamwidth = dscfg.get('beamwidthv', None)
    else:
        rcs_field = 'radar_cross_section_hh'

        beamwidth = dscfg.get('beamwidthh', None)

    pulse_width = dscfg.get('PulseWidth', None)
    kw2 = dscfg.get('kw2', 0.93)

    rcs_dict = pyart.retrieve.compute_rcs(
        radar, kw2=kw2, pulse_width=pulse_width, beamwidth=beamwidth,
        refl_field=refl_field, rcs_field=rcs_field)

    # prepare for exit
    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()
    new_dataset['radar_out'].add_field(rcs_field, rcs_dict)

    return new_dataset, ind_rad


def process_vol_refl(procstatus, dscfg, radar_list=None):
    """
    Computes the volumetric reflectivity in 10log10(cm^2 km^-3)

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : list of string. Dataset keyword
            The input data types
        freq : float. Dataset keyword
            The radar frequency
        kw : float. Dataset keyword
            The water constant
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """
    if procstatus != 1:
        return None, None

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
        if datatype == 'dBZ':
            refl_field = 'reflectivity'
        if datatype == 'dBuZ':
            refl_field = 'unfiltered_reflectivity'
        if datatype == 'dBZc':
            refl_field = 'corrected_reflectivity'
        if datatype == 'dBuZc':
            refl_field = 'corrected_unfiltered_reflectivity'
        if datatype == 'dBZv':
            refl_field = 'reflectivity_vv'
        if datatype == 'dBuZv':
            refl_field = 'unfiltered_reflectivity_vv'
        if datatype == 'dBuZvc':
            refl_field = 'corrected_unfiltered_reflectivity_vv'

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    if refl_field not in radar.fields:
        warn('Unable to obtain signal power. Missing field '+refl_field)
        return None, None

    if refl_field.endswith('_vv'):
        vol_refl_field = 'volumetric_reflectivity_vv'
    else:
        vol_refl_field = 'volumetric_reflectivity'

    freq = dscfg.get('freq', None)
    kw = dscfg.get('kw', None)

    vol_refl_dict = pyart.retrieve.compute_vol_refl(
        radar, kw=kw, freq=freq, refl_field=refl_field,
        vol_refl_field=vol_refl_field)

    # prepare for exit
    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()
    new_dataset['radar_out'].add_field(vol_refl_field, vol_refl_dict)

    return new_dataset, ind_rad


def process_snr(procstatus, dscfg, radar_list=None):
    """
    Computes SNR

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : string. Dataset keyword
            The input data type
        output_type : string. Dataset keyword
            The output data type. Either SNRh or SNRv
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """

    if procstatus != 1:
        return None, None

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
        if datatype == 'dBZ':
            refl = 'reflectivity'
        if datatype == 'dBuZ':
            refl = 'unfiltered_reflectivity'
        if datatype == 'dBZv':
            refl = 'reflectivity_vv'
        if datatype == 'dBuZv':
            refl = 'unfiltered_reflectivity_vv'
        if datatype == 'Nh':
            noise = 'noisedBZ_hh'
        if datatype == 'Nv':
            noise = 'noisedBZ_vv'

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    if (refl not in radar.fields) or (noise not in radar.fields):
        warn('Unable to compute SNR. Missing data')
        return None, None

    output_type = dscfg.get('output_type', 'SNRh')
    if output_type == 'SNRh':
        snr_field = 'signal_to_noise_ratio_hh'
    else:
        snr_field = 'signal_to_noise_ratio_vv'

    snr = pyart.retrieve.compute_snr(
        radar, refl_field=refl, noise_field=noise,
        snr_field=snr_field)

    # prepare for exit
    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()
    new_dataset['radar_out'].add_field(snr_field, snr)

    return new_dataset, ind_rad


def process_l(procstatus, dscfg, radar_list=None):
    """
    Computes L parameter

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : string. Dataset keyword
            The input data type
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """

    if procstatus != 1:
        return None, None

    radarnr, _, datatype, _, _ = get_datatype_fields(dscfg['datatype'])
    rhohv = get_fieldname_pyart(datatype)

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    if rhohv not in radar.fields:
        print('Unable to compute L. Missing RhoHV field')
        return None, None

    l = pyart.retrieve.compute_l(
        radar, rhohv_field=rhohv,
        l_field='logarithmic_cross_correlation_ratio')

    # prepare for exit
    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()
    new_dataset['radar_out'].add_field(
        'logarithmic_cross_correlation_ratio', l)

    return new_dataset, ind_rad


def process_cdr(procstatus, dscfg, radar_list=None):
    """
    Computes Circular Depolarization Ratio

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : string. Dataset keyword
            The input data type
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """

    if procstatus != 1:
        return None, None

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
        if datatype == 'RhoHV':
            rhohv = 'cross_correlation_ratio'
        if datatype == 'uRhoHV':
            rhohv = 'uncorrected_cross_correlation_ratio'
        if datatype == 'RhoHVu':
            rhohv = 'unfiltered_cross_correlation_ratio'
        if datatype == 'ZDR':
            zdr = 'differential_reflectivity'
        if datatype == 'ZDRc':
            zdr = 'corrected_differential_reflectivity'

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    if ((rhohv not in radar.fields) or
            (zdr not in radar.fields)):
        warn('Unable to compute CDR field. Missing data')
        return None, None

    cdr = pyart.retrieve.compute_cdr(
        radar, rhohv_field=rhohv, zdr_field=zdr,
        cdr_field='circular_depolarization_ratio')

    # prepare for exit
    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()
    new_dataset['radar_out'].add_field('circular_depolarization_ratio', cdr)

    return new_dataset, ind_rad


def process_rainrate(procstatus, dscfg, radar_list=None):
    """
    Estimates rainfall rate from polarimetric moments

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : string. Dataset keyword
            The input data type
        RR_METHOD : string. Dataset keyword
            The rainfall rate estimation method. One of the following:
            Z, ZPoly, KDP, A, ZKDP, ZA, hydro
        alpha, beta : float
            factor and exponent of the R-Var power law R = alpha*Var^Beta.
            Default value depending on RR_METHOD. Z (0.0376, 0.6112),
            KDP (None, None), A (None, None)
        alphaz, betaz : float
            factor and exponent of the R-Z power law R = alpha*Z^Beta.
            Default value (0.0376, 0.6112)
        alphazr, betazr : float
            factor and exponent of the R-Z power law R = alpha*Z^Beta applied
            to rain in method hydro. Default value (0.0376, 0.6112)
        alphazs, betazs : float
            factor and exponent of the R-Z power law R = alpha*Z^Beta applied
            to solid precipitation in method hydro. Default value (0.1, 0.5)
        alphakdp, betakdp : float
            factor and exponent of the R-KDP power law R = alpha*KDP^Beta.
            Default value (None, None)
        alphaa, betaa : float
            factor and exponent of the R-Ah power law R = alpha*Ah^Beta.
            Default value (None, None)
        thresh : float
            In hybrid methods, Rainfall rate threshold at which the retrieval
            method used changes [mm/h]. Default value depending on RR_METHOD.
            ZKDP 10, ZA 10, hydro 10
        mp_factor : float
            Factor by which the Z-R relation is multiplied in the melting layer
            in method hydro. Default 0.6
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """

    if procstatus != 1:
        return None, None

    if 'RR_METHOD' not in dscfg:
        raise Exception(
            "ERROR: Undefined parameter 'RR_METHOD' for dataset '%s'"
            % dscfg['dsname'])

    if dscfg['RR_METHOD'] == 'Z':
        radarnr, _, datatype, _, _ = get_datatype_fields(dscfg['datatype'][0])
        refl_field = get_fieldname_pyart(datatype)

        ind_rad = int(radarnr[5:8])-1
        if radar_list[ind_rad] is None:
            warn('No valid radar')
            return None, None
        radar = radar_list[ind_rad]

        if refl_field not in radar.fields:
            warn('ERROR: Unable to compute rainfall rate. Missing data')
            return None, None

        # user defined parameters
        alpha = dscfg.get('alpha', 0.0376)
        beta = dscfg.get('beta', 0.6112)

        rain = pyart.retrieve.est_rain_rate_z(
            radar, alpha=alpha, beta=beta, refl_field=refl_field,
            rr_field=None)

    elif dscfg['RR_METHOD'] == 'ZPoly':
        radarnr, _, datatype, _, _ = get_datatype_fields(dscfg['datatype'][0])
        refl_field = get_fieldname_pyart(datatype)

        ind_rad = int(radarnr[5:8])-1
        if radar_list[ind_rad] is None:
            warn('No valid radar')
            return None, None
        radar = radar_list[ind_rad]

        if refl_field not in radar.fields:
            warn('Unable to compute rainfall rate. Missing data')
            return None, None

        rain = pyart.retrieve.est_rain_rate_zpoly(
            radar, refl_field=refl_field, rr_field=None)

    elif dscfg['RR_METHOD'] == 'KDP':
        radarnr, _, datatype, _, _ = get_datatype_fields(dscfg['datatype'][0])
        kdp_field = get_fieldname_pyart(datatype)

        ind_rad = int(radarnr[5:8])-1
        if radar_list[ind_rad] is None:
            warn('No valid radar')
            return None, None
        radar = radar_list[ind_rad]

        if kdp_field not in radar.fields:
            warn('Unable to compute rainfall rate. Missing data')
            return None, None

        # user defined parameters
        alpha = dscfg.get('alpha', None)
        beta = dscfg.get('beta', None)

        rain = pyart.retrieve.est_rain_rate_kdp(
            radar, alpha=alpha, beta=beta, kdp_field=kdp_field, rr_field=None)

    elif dscfg['RR_METHOD'] == 'A':
        radarnr, _, datatype, _, _ = get_datatype_fields(dscfg['datatype'][0])
        a_field = get_fieldname_pyart(datatype)

        ind_rad = int(radarnr[5:8])-1
        if radar_list[ind_rad] is None:
            warn('No valid radar')
            return None, None
        radar = radar_list[ind_rad]

        if a_field not in radar.fields:
            warn('Unable to compute rainfall rate. Missing data')
            return None, None

        # user defined parameters
        alpha = dscfg.get('alpha', None)
        beta = dscfg.get('beta', None)

        rain = pyart.retrieve.est_rain_rate_a(
            radar, alpha=alpha, beta=beta, a_field=a_field, rr_field=None)

    elif dscfg['RR_METHOD'] == 'ZKDP':
        for datatypedescr in dscfg['datatype']:
            radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
            if datatype == 'dBZc':
                refl_field = 'corrected_reflectivity'
            if datatype == 'KDPc':
                kdp_field = 'corrected_specific_differential_phase'
            if datatype == 'dBZ':
                refl_field = 'reflectivity'
            if datatype == 'KDP':
                kdp_field = 'specific_differential_phase'

        ind_rad = int(radarnr[5:8])-1
        if radar_list[ind_rad] is None:
            warn('No valid radar')
            return None, None
        radar = radar_list[ind_rad]

        if ((refl_field not in radar.fields) or
                (kdp_field not in radar.fields)):
            warn('Unable to compute rainfall rate. Missing data')
            return None, None

        # user defined parameters
        alphaz = dscfg.get('alphaz', 0.0376)
        betaz = dscfg.get('betaz', 0.6112)
        alphakdp = dscfg.get('alphakdp', None)
        betakdp = dscfg.get('betakdp', None)
        thresh = dscfg.get('thresh', 10.)

        rain = pyart.retrieve.est_rain_rate_zkdp(
            radar, alphaz=alphaz, betaz=betaz, alphakdp=alphakdp,
            betakdp=betakdp, refl_field=refl_field, kdp_field=kdp_field,
            rr_field=None, master_field=refl_field, thresh=thresh,
            thresh_max=True)

    elif dscfg['RR_METHOD'] == 'ZA':
        for datatypedescr in dscfg['datatype']:
            radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
            if datatype == 'dBZc':
                refl_field = 'corrected_reflectivity'
            if datatype == 'Ahc':
                a_field = 'corrected_specific_attenuation'
            if datatype == 'dBZ':
                refl_field = 'reflectivity'
            if datatype == 'Ah':
                a_field = 'specific_attenuation'

        ind_rad = int(radarnr[5:8])-1
        if radar_list[ind_rad] is None:
            warn('No valid radar')
            return None, None
        radar = radar_list[ind_rad]

        if ((refl_field not in radar.fields) or
                (a_field not in radar.fields)):
            warn('Unable to compute rainfall rate. Missing data')
            return None, None

        # user defined parameters
        alphaz = dscfg.get('alphaz', 0.0376)
        betaz = dscfg.get('betaz', 0.6112)
        alphaa = dscfg.get('alphaa', None)
        betaa = dscfg.get('betaa', None)
        thresh = dscfg.get('thresh', 5.)

        rain = pyart.retrieve.est_rain_rate_za(
            radar, alphaz=alphaz, betaz=betaz, alphaa=alphaa, betaa=betaa,
            refl_field=refl_field, a_field=a_field, rr_field=None,
            master_field=refl_field, thresh=thresh, thresh_max=True)

    elif dscfg['RR_METHOD'] == 'hydro':
        for datatypedescr in dscfg['datatype']:
            radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
            if datatype == 'dBZc':
                refl_field = 'corrected_reflectivity'
            if datatype == 'Ahc':
                a_field = 'corrected_specific_attenuation'
            if datatype == 'hydro':
                hydro_field = 'radar_echo_classification'
            if datatype == 'dBZ':
                refl_field = 'reflectivity'
            if datatype == 'Ah':
                a_field = 'specific_attenuation'

        ind_rad = int(radarnr[5:8])-1
        if radar_list[ind_rad] is None:
            warn('No valid radar')
            return None, None
        radar = radar_list[ind_rad]

        # user defined parameters
        alphazr = dscfg.get('alphazr', 0.0376)
        betazr = dscfg.get('betazr', 0.6112)
        alphazs = dscfg.get('alphazs', 0.1)
        betazs = dscfg.get('betazs', 0.5)
        alphaa = dscfg.get('alphaa', None)
        betaa = dscfg.get('betaa', None)
        thresh = dscfg.get('thresh', 5.)
        mp_factor = dscfg.get('mp_factor', 0.6)

        if ((refl_field in radar.fields) and
                (a_field in radar.fields) and
                (hydro_field in radar.fields)):
            rain = pyart.retrieve.est_rain_rate_hydro(
                radar, alphazr=alphazr, betazr=betazr, alphazs=alphazs,
                betazs=betazs, alphaa=alphaa, betaa=betaa,
                mp_factor=mp_factor, refl_field=refl_field, a_field=a_field,
                hydro_field=hydro_field, rr_field=None,
                master_field=refl_field, thresh=thresh, thresh_max=True)
        elif refl_field in radar.fields:
            warn('Unable to compute rainfall rate using hydrometeor ' +
                 'classification. Missing data. ' +
                 'A simple Z-R relation will be used instead')
            rain = pyart.retrieve.est_rain_rate_z(
                radar, alpha=alphazr, beta=betazr, refl_field=refl_field,
                rr_field=None)
        else:
            warn('Unable to compute rainfall rate using hydrometeor ' +
                 'classification. Missing data.')
            return None, None
    else:
        raise Exception(
            "ERROR: Unknown rainfall rate retrieval method " +
            dscfg['RR_METHOD'])

    # prepare for exit
    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()
    new_dataset['radar_out'].add_field('radar_estimated_rain_rate', rain)

    return new_dataset, ind_rad


def process_bird_density(procstatus, dscfg, radar_list=None):
    """
    Computes the bird density from the volumetric reflectivity

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : list of string. Dataset keyword
            The input data types
        sigma_bird : float. Dataset keyword
            The bird radar cross section
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """
    if procstatus != 1:
        return None, None

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
        if datatype == 'eta_h':
            vol_refl_field = 'volumetric_reflectivity'
        if datatype == 'eta_v':
            vol_refl_field = 'volumetric_reflectivity_vv'

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    if vol_refl_field not in radar.fields:
        warn('Unable to obtain bird density. Missing field '+vol_refl_field)
        return None, None

    sigma_bird = dscfg.get('sigma_bird', 11.)
    bird_density_dict = pyart.retrieve.compute_bird_density(
        radar, sigma_bird=sigma_bird, vol_refl_field=vol_refl_field,
        bird_density_field='bird_density')

    # prepare for exit
    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()
    new_dataset['radar_out'].add_field('bird_density', bird_density_dict)

    return new_dataset, ind_rad
