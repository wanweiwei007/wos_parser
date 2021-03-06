#!/usr/bin/env python

import logging
import gzip
from shutil import copyfileobj
from os import listdir
from os.path import isfile, join
from .parse import parse_wos_xml, xml_remove_trivial_namespace
from .chunkflusher import ChunkFlusher

log_levels = {
    "DEBUG": logging.DEBUG, "INFO": logging.INFO,
    "WARNING": logging.WARNING, "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
    }


def gunzip_file(fname_in, fname_out):
    with gzip.open(fname_in, 'rb') as f_in:
        with open(fname_out, 'wb') as f_out:
            copyfileobj(f_in, f_out)


def main(sourcepath, destpath, global_year, chunksize=100000, maxchunks=None, ntest=None):

    only_gz_files = [f for f in listdir(sourcepath) if isfile(join(sourcepath, f)) and f[-3:] == '.gz']

    good_prefix = join(destpath, 'good_{0}_'.format(global_year))
    bad_prefix = join(destpath, 'bad_{0}_'.format(global_year))
    good_cf = ChunkFlusher(good_prefix, chunksize, maxchunks)
    bad_cf = ChunkFlusher(bad_prefix, chunksize, maxchunks)

    for f in only_gz_files:
        if good_cf.ready() and bad_cf.ready():
            full_f = join(sourcepath, f)
            f_degz = join(sourcepath, f[:-3])
            gunzip_file(full_f, f_degz)
            xml_remove_trivial_namespace(f_degz)
            with open(f_degz, 'rb') as fp:
                parse_wos_xml(fp, global_year, good_cf, bad_cf, ntest)

    # terminal flush
    good_cf.flush_chunk()
    bad_cf.flush_chunk()
    logging.error('not an error : {0} good records, '
                  '{1} bad records'.format(good_cf.items_processed(),
                                           bad_cf.items_processed()))
