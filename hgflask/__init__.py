# -*- coding: utf-8 -*-
import base64
import bbi
import cooler
import cytoolz as toolz
import hgtiles.bed2ddb as hgb2
import hgtiles.cooler as hgco
import hgtiles.hitile as hghi
import math
import numpy as np
import pandas as pd
import sys

from .tilesets.bigwig_tiles import get_quadtree_depth, get_chromsizes, get_bigwig_tile

from flask import Flask
from flask import request, jsonify
#from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS

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

TILESETS = []
# TILESETS = [{  
#     'uuid': "abc",
#     'filetype': "bigwig",
#     'datatype': "vector",
#     'url': 'http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeSydhTfbs/wgEncodeSydhTfbsGm12878Ctcfsc15914c20StdSig.bigWig',
#     'private': False,
#     'name': "blabla",
#     'coordSystem': "hg19",
#     'coordSystem2': "hg19",
#     'created': "2017-02-02T21:10:56.265085Z",
# }]


def bigwig_tsinfo(bwpath):
    '''
    Get the tileset info for a bigWig file

    Parameters
    ----------
    tileset: tilesets.models.Tileset object
        The tileset that the tile ids should be retrieved from

    Returns
    -------
    tileset_info: {'min_pos': [], 
                    'max_pos': [], 
                    'tile_size': 1024, 
                    'max_zoom': 7
                    }
    '''
    TILE_SIZE = 1024
    chromsizes = bbi.chromsizes(bwpath)
    chromosomes = cooler.util.natsorted(chromsizes.keys())
    chromsizes = pd.Series(chromsizes)[chromosomes]
    min_tile_cover = np.ceil(sum(chromsizes) / TILE_SIZE)
    max_zoom = int(np.ceil(np.log2(min_tile_cover)))
    tileset_info = {
        'min_pos': [0],
        'max_pos': [TILE_SIZE * 2 ** max_zoom],
        'max_width': TILE_SIZE * 2 ** max_zoom,
        'tile_size': TILE_SIZE,
        'max_zoom': max_zoom
    }
    return tileset_info


def bigwig_tiles(bwpath, tile_ids):
    '''
    Generate tiles from a bigwig file.

    Parameters
    ----------
    tileset: tilesets.models.Tileset object
        The tileset that the tile ids should be retrieved from
    tile_ids: [str,...]
        A list of tile_ids (e.g. xyx.0.0) identifying the tiles
        to be retrieved

    Returns
    -------
    tile_list: [(tile_id, tile_data),...]
        A list of tile_id, tile_data tuples
    '''
    TILE_SIZE = 1024
    generated_tiles = []
    for tile_id in tile_ids:
        tile_id_parts = tile_id.split('.')
        tile_position = list(map(int, tile_id_parts[1:3]))
        zoom_level = tile_position[0]
        tile_pos = tile_position[1]
        
        # this doesn't combine multiple consequetive ids, which
        # would speed things up
        max_depth = get_quadtree_depth(get_chromsizes(bwpath))
        tile_size = TILE_SIZE * 2 ** (max_depth - zoom_level)
        start_pos = tile_pos * tile_size
        end_pos = start_pos + tile_size
        dense = get_bigwig_tile(bwpath, zoom_level, start_pos, end_pos)

        if len(dense):
            max_dense = max(dense)
            min_dense = min(dense)
        else:
            max_dense = 0
            min_dense = 0

        min_f16 = np.finfo('float16').min
        max_f16 = np.finfo('float16').max

        has_nan = len([d for d in dense if np.isnan(d)]) > 0

        if (
            not has_nan and
            max_dense > min_f16 and max_dense < max_f16 and
            min_dense > min_f16 and min_dense < max_f16
        ):
            tile_value = {
                'dense': base64.b64encode(dense.astype('float16')).decode('utf-8'),
                'dtype': 'float16'
            }
        else:
            tile_value = {
                'dense': base64.b64encode(dense.astype('float32')).decode('utf-8'),
                'dtype': 'float32'
            }

        generated_tiles += [(tile_id, tile_value)]
    return generated_tiles


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


@app.route('/api/v1/tileset_info/', methods=['GET'])
def tileset_info():
    uuids = request.args.getlist("d")

    info = {}
    for uuid in uuids:
        ts = next((ts for ts in TILESETS if ts['uuid'] == uuid), None)
        
        if ts is not None:
            info[uuid] = ts.copy()
            if info[uuid]['filetype'] == 'bigwig':
                info[uuid].update(bigwig_tsinfo(ts['url']))                
            elif info[uuid]['filetype'] == 'cooler':
                info[uuid].update(hgco.tileset_info(ts['filepath']))
            elif info[uuid]['filetype'] == 'hitile':
                info[uuid].update(hghi.tileset_info(ts['filepath']))
            elif ts['filetype'] == 'bedarcsdb':
                tiles.extend(hgb2.get_2d_tileset_info(ts['filepath'], tids))
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
            if ts['filetype'] == 'bigwig':
                tiles.extend(bigwig_tiles(ts['url'], tids))
            elif ts['filetype'] == 'cooler':
                tiles.extend(hgco.tiles(ts['filepath'], tids))
            elif ts['filetype'] == 'hitile':
                tiles.extend(hghi.tiles(ts['filepath'], tids))
            elif ts['filetype'] == 'bedarcsdb':
                print('tids:', tids)
                tiles.extend(hgb2.get_1D_tiles(ts['filepath'], tids))
            else:
                print("Unknown filetype:", ts['filetype'], file=sys.stderr)

    data = {tid: tval for tid, tval in tiles}
    return jsonify(data)



# if __name__ == '__main__':
#     app.run(debug=True, port=5000)

    # import threading
    # from functools import partial
    # t = threading.Thread(target=partial(app.run, debug=True, port=5000))
