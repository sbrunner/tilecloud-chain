# -*- coding: utf-8 -*-

# Copyright (c) 2013 by Stéphane Brunner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 3. Neither the name of Camptocamp nor the names of its contributors may
# be used to endorse or promote products derived from this software
# without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from tilecloud import Tile, TileCoord
from tilecloud_chain import TileGeneration

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPNoContent


class Serve(TileGeneration):

    def __init__(self, request):
        self.request = request
        self.settings = request.registry.settings

        self.tilegeneration = TileGeneration(self.settings['tilegeneration_configfile'])
        self.cache = self.tilegeneration.caches[
            self.settings['tilegeneration_cache'] if 'tilegeneration_cache' in self.settings
            else self.tilegeneration.config['generation']['default_cache']
        ]
        self.stores = {}
        self.strict = 'strict' in self.settings and self.settings['strict']

    def _get(self, path, cache):
        if cache['type'] == 's3':  # pragma: no cover
            s3bucket = S3Connection().bucket(cache['bucket'])
            s3key = s3bucket.key(('%(folder)s' % cache) + path)
            return s3key.get().body
        else:
            folder = cache['folder'] or ''
            filename = folder + path
            directory = os.path.dirname(filename)
            f = open(folder + path, 'rb')
            data = f.read()
            f.close()
            return data

    def __call__(self):
        params = {}
        dimensions = None
        if 'path' in self.request.matchdict:
            path = self.request.matchdict['path']
            if len(path) < 7:
                if '/'.join(path) == cache['wmtscapabilities_file'][1:]:
                    self.request.response.body_file = self._get(cache['wmtscapabilities_file'])
                    self.request.response.content_type = "application/xml"
                    return
                else:
                    raise HTTPBadRequest("Not enough path")
            else:
                params['service'] = 'WMTS'
                params['request'] = 'GetTile'
                params['version'] = path[0]

                last = path[-1].split('.')
                params['format'] = last[1]
                params['layer'] = path[1]
                params['style'] = path[2]
                dimensions = [('Dimension', v) for v in path[3:-4]]
                params['tilematrixset'] = path[-4]
                params['tilematrix'] = path[-3]
                params['tilerow'] = path[-2]
                params['tilecol'] = last[0]
        else:
            for param, value in self.request.params.items():
                params[param.lower()] = value

                if \
                    not 'service' in params or \
                    not 'request' in params or \
                    not 'version' in params or \
                    not 'format' in params or \
                    not 'layer' in params or \
                    not 'tilematrixset' in params or \
                    not 'tilematrix' in params or \
                    not 'tilerow' in params or \
                    not 'tilecol' in params:
                    raise HTTPBadRequest("Not all required parameters are present")

        if self.strict:
            if params['service'] != 'WMTS':
                raise HTTPBadRequest("Wrong Service '%s'" % params['service'])
            if params['request'] != 'GetTile':
                raise HTTPBadRequest("Wrong Request '%s'" % params['request'])
            if params['version'] != '1.0.0':
                raise HTTPBadRequest("Wrong Version '%s'" % params['version'])

        if params['layer'] in self.tilegeneration.layers:
            layer = self.tilegeneration.layers[params['layer']]
        else:
            raise HTTPBadRequest("Wrong Layer '%s'" % params['version'])

        if self.strict:
            if params['format'] != layer['extension']:
                raise HTTPBadRequest("Wrong Format '%s'" % params['format'])
            if params['style'] != layer['wmts_style']:
                raise HTTPBadRequest("Wrong Style '%s'" % params['style'])
            if params['tilematrixset'] != layer['grid']:
                raise HTTPBadRequest("Wrong TileMatrixSet '%s'" % params['tilematrixset'])

        store_ref = [
            params['layer'],
            params['style'],
            params['tilematrixset'],
            params['format'],
        ]

        if 'path' not in self.request.matchdict:
            dimensions = []
            for dimension in layer['dimensions']:
                value = \
                    params[dimension['name'].lower()] \
                    if dimension['name'].lower() in params \
                    else dimension['default']
                dimensions.append((dimension['name'], value))
                store_ref.extend((dimension['name'], value))

        store_ref = '/'.join(store_ref)
        if store_ref in self.stores:
            store = self.stores[store_ref]  # pragma: no cover
        else:
            if self.strict:
                store = self.tilegeneration.get_store(self.cache, layer, dimensions)
            else:
                mime = {
                    'png': 'image/png',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'json': 'application/json',
                }
                store = self.tilegeneration.get_store(self.cache, {
                    'name': params['layer'],
                    'wmts_style': params['style'],
                    'grid': params['tilematrixset'],
                    'extension': params['format'],
                    'mime_type': mime[params['format']],
                }, dimensions)

        tile = Tile(TileCoord(
            # TODO fix for matrix_identifier = resolution
            int(params['tilematrix']),
            int(params['tilecol']),
            int(params['tilerow']),
        ))
        tile = store.get_one(tile)
        if tile:
            self.request.response.body = tile.data
            self.request.response.content_type = tile.content_type
            return self.request.response
        else:
            raise HTTPNoContent()
