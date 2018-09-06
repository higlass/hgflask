# -*- coding: utf-8 -*-
import base64
import bbi
import cooler
import cytoolz as toolz
import functools as ft
import json
import requests
import slugid
import multiprocessing as mp

import hgtiles.bed2ddb as hgb2
import hgtiles.cooler as hgco
import hgtiles.hitile as hghi
import hgtiles.bigwig as hgbi
import hgtiles.files as hgfi

import math
import numpy as np
import pandas as pd
import sys
import time

from .tilesets.bigwig_tiles import get_quadtree_depth, get_chromsizes, get_bigwig_tile

from flask import Flask
from flask import request, jsonify
#from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS


def create_app(tilesets, external_filetype_handlers=None):
    app = Flask(__name__)
    CORS(app)

    CHROMSIZES = {
        'hg19': {
            "chr1": {"size": 249250621}, 
            "chr2": {"size": 243199373}, 
            "chr3": {"size": 198022430}, 
            "chr4": {"size": 191154276}, 
            "chr5": {"size": 180915260}, 
            "chr6": {"size": 171115067}, 
            "chr7": {"size": 159138663}, 
            "chr8": {"size": 146364022}, 
            "chr9": {"size": 141213431}, 
            "chr10": {"size": 135534747}, 
            "chr11": {"size": 135006516}, 
            "chr12": {"size": 133851895}, 
            "chr13": {"size": 115169878}, 
            "chr14": {"size": 107349540}, 
            "chr15": {"size": 102531392}, 
            "chr16": {"size": 90354753}, 
            "chr17": {"size": 81195210}, 
            "chr18": {"size": 78077248}, 
            "chr19": {"size": 59128983}, 
            "chr20": {"size": 63025520}, 
            "chr21": {"size": 48129895}, 
            "chr22": {"size": 51304566}, 
            "chrX": {"size": 155270560}, 
            "chrY": {"size": 59373566}, 
            "chrM": {"size": 16571},
        },
    }

    TILESETS = tilesets

    #############
    ### VIEWS ###
    #############


    @app.route('/api/v1/')
    def hello():
        return("Hello World!")


    @app.route('/api/v1/available-chrom-sizes/', methods=['GET'])
    def available_chrom_sizes():
        return jsonify({
            "count": len(CHROMSIZES), 
            "results": {i: CHROMSIZES[i] for i in range(len(CHROMSIZES))}
        })


    @app.route('/api/v1/chrom-sizes/', methods=['GET'])
    def chrom_sizes():
        uuid = request.args.get('id', None)
        res_type = request.args.get('type', 'json')
        incl_cum = request.args.get('cum', False)
        
        if uuid is None:
            return jsonify(CHROMSIZES)

        try:
            data = CHROMSIZES[uuid]
        except KeyError:
            return jsonify({"error": "Not found"}), 404

        if incl_cum:
            cum = 0
            for chrom in data.keys():   # dictionaries in py3.6+ are ordered!
                data[chrom]['offset'] = cum
                cum += data[chrom]['size']

        if res_type == 'json':
            return jsonify(data)

        elif res_type == 'csv':
            if incl_cum:
               return '\n'.join('{}\t{}\t{}'.format(chrom, row['size'], row['offset'])
                    for chrom, row in data.items())
            else:
                return '\n'.join('{}\t{}'.format(chrom, row['size'])
                    for chrom, row in data.items())

        else:
            return jsonify({"error": "Unknown response type"}), 500


    @app.route('/api/v1/uids_by_filename/', methods=['GET'])
    def uids_by_filename():
        return jsonify({
            "count": len(TILESETS), 
            "results": {i: TILESETS[i] for i in range(len(TILESETS))}
        })


    @app.route('/api/v1/tilesets/', methods=['GET'])
    def tilesets():
        return jsonify({
            "count": len(TILESETS),
            "next": None,
            "previous": None,
            "results": TILESETS,
        })

    def get_filepath(tileset_def):
        '''
        Get the filepath from a tileset definition

        Parameters
        ----------
        tileset_def: { 'filepath': ..., 'uid': ..., 'filetype': ...}
            The tileset definition     
        returns: string
            The filepath, either as specified in the tileset_def or
            None
        '''
        if 'filepath' in tileset_def:
            return tileset_def['filepath']

        return None

    def get_filetype(tileset_def):
        '''
        Get the filetype for the given dataset.

        Parameters
        ----------
        tileset_def: { 'filepath': ..., 'uid': ..., 'filetype': ...}
            The tileset definition     
        returns: string
            The filetype, either as specified in the tileset_def or
            inferred
        '''
        if 'filetype' in tileset_def:
            return tileset_def['filetype']

        return hgfi.infer_filetype(tileset_def['filepath'])

    @app.route('/api/v1/tileset_info/', methods=['GET'])
    def tileset_info():
        uuids = request.args.getlist("d")

        info = {}
        for uuid in uuids:
            ts = next((ts for ts in TILESETS if ts['uuid'] == uuid), None)
            
            if ts is not None:
                info[uuid] = ts.copy()

                # see if there's a filepath provided
                if 'filepath' in info[uuid]:
                    filepath = info[uuid]['filepath']
                else:
                    filepath = None

                filetype = get_filetype(info[uuid])
                print('filetype:', filetype)

                if filetype in external_filetype_handlers:
                    handler = external_filetype_handlers[filetype]['tileset_info']
                    if filepath is not None:
                        info[uuid].update(handler(filepath))
                    else:
                        info[uuid].update(handler())
                elif filetype == 'bigwig':
                    info[uuid].update(hgbi.tileset_info(filepath))                
                elif filetype == 'cooler':
                    info[uuid].update(hgco.tileset_info(filepath))
                elif filetype == 'hitile':
                    info[uuid].update(hghi.tileset_info(filepath))
                elif filetype == 'bedarcsdb':
                    tiles.extend(hgb2.get_2d_tileset_info(filepath))
                else:
                    print("Unknown filetype:", info[uuid]['filetype'], 
                            file=sys.stderr)
            else:
                info[uuid] = {
                    'error': 'No such tileset with uid: {}'.format(uuid)
                }

        return jsonify(info)


    @app.route('/api/v1/tiles/', methods=['GET'])
    def tiles():
        tids_requested = set(request.args.getlist("d"))
        
        if not tids_requested:
            return jsonify({'error': 'No tiles requested'}), 400
        
        extract_uuid = lambda tid: tid.split('.')[0]
        uuids_to_tids = toolz.groupby(extract_uuid, tids_requested)
        
        tiles = []
        for uuid, tids in uuids_to_tids.items():
            ts = next((ts for ts in TILESETS if ts['uuid'] == uuid), None)
            if ts is not None:
                filetype = get_filetype(ts)
                filepath = get_filepath(ts)

                if filetype in external_filetype_handlers:
                    handler = external_filetype_handlers[filetype]['tiles']
                    if filepath is not None:
                        tiles.extend(handler(filepath, tids))
                    else:
                        tiles.extend(handler(tids))
                elif filetype == 'bigwig':
                    tiles.extend(hgbi.tiles(filepath, tids))
                elif filetype == 'cooler':
                    tiles.extend(hgco.tiles(filepath, tids))
                elif filetype == 'hitile':
                    tiles.extend(hghi.tiles(filepath, tids))
                elif filetype == 'bedarcsdb':
                    print('tids:', tids)
                    tiles.extend(hgb2.get_1D_tiles(filepath, tids))
                else:
                    print("Unknown filetype:", filetype, file=sys.stderr)

        data = {tid: tval for tid, tval in tiles}
        return jsonify(data)

    # if __name__ == '__main__':
    #     app.run(debug=True, port=5000)

        # import threading
        # from functools import partial
        # t = threading.Thread(target=partial(app.run, debug=True, port=5000))

    return app

def get_open_port():
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("",0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        return port

class RunningServer():
    def __init__(self, port, process):
        '''
        Maintain a reference to a running higlass server

        Parameters:
        ----------
        port: int
            The port that this server is running on
        process: Popen.process
            The process running the server
        '''
        self.port = port
        self.process = process

    def tileset_info(self, uid):
        '''
        Return the tileset info for the given tileset
        '''
        url = 'http://localhost:{port}/api/v1/tileset_info/?d={uid}'.format(
                port=self.port, uid=uid)

        req = requests.get(url)
        if req.status_code != 200:
            raise Exception('Error fetching tileset_info:', req.content)

        content = json.loads(req.content)
        return content[uid]

    def tiles(self, uid, z, x, y=None):
        '''
        Return tiles from the specified dataset (uid) at
        the given position (z,x,[u])
        '''
        tile_id ='{uid}.{z}.{x}'.format(uid=uid, z=z, x=x)
        if y is not None:
            tile_id += '.{y}'.format(y=y)
        url = 'http://localhost:{port}/api/v1/tiles/?d={tile_id}'.format(
                port=self.port, tile_id=tile_id)

        req = requests.get(url)
        if req.status_code != 200:
            raise Exception('Error fetching tile:', req.content)

        content = json.loads(req.content)
        return content[tile_id]

    def stop(self):
        '''
        Stop this server so that the calling process can exit
        '''
        self.process.terminate()

'''
Keep track of the server processes that have been started.
So that when someone says 'start', the old ones are terminated
'''
processes = {}

def start(tilesets, port=None, filetype_handlers={}):
    '''
    Start the hgflask server.

    Parameters
    ----------
    tilesets: object
        The list of tilesets to serve. For example:
        TILESETS = [{  
            'uuid': "abc",
            'filetype': "grid_1000",
            'datatype': "matrix",
        },
        {  
            'uuid': "abc1",
            'filetype': "grid_8000",
            'datatype': "matrix",
        },
        ]
    port: int
        The port to start this server on. If it is None, a port
        will automatically be assigned.

    filetype_handlers: dict
        A dictionary of handlers for filetypes not supported out of the
        box
    '''

    global processes

    print("processes:", processes)
    to_delete = []

    for puid in processes:
        print("terminating:", puid)
        processes[puid].terminate()
        to_delete += [puid]

    for puid in to_delete:
        del processes[puid]

    # we're going to assign a uuid to each server process so that if anything
    # goes wrong, the variable referencing the process doesn't get lost
    app = create_app(tilesets=tilesets, external_filetype_handlers=filetype_handlers)# we're going to assign a uuid to each server process so that if anything
    # goes wrong, the variable referencing the process doesn't get lost
    app = create_app(tilesets=tilesets, external_filetype_handlers=filetype_handlers)

    port=get_open_port() if port is None else port

    uuid = slugid.nice().decode('utf8')
    processes[uuid] = mp.Process(
        target=ft.partial(app.run, 
                          debug=True, 
                          port=port, 
                          host='0.0.0.0',
                          use_reloader=False))

    processes[uuid].start()

    connected = False
    while not connected:
        try:
            ret = requests.get('http://localhost:{}/api/v1/tileset_info/?d=x'.format(port))
            connected = True
        except Exception as err:
            print('sleeping')
            time.sleep(.2)
            pass

    return RunningServer(port, processes[uuid])
    print("processes", processes)
