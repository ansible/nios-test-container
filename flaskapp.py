#!/usr/bin/env python

# https://www.infoblox.com/wp-content/uploads/infoblox-deployment-infoblox-rest-api.pdf

from flask import Flask
from flask import jsonify
from flask import request
from flask_basicauth import BasicAuth
from pprint import pprint



app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'infoblox'
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app)


class NetworkView(object):
    viewtype = None
    uid = None
    is_default = False
    name = None
    comment = None
    extattrs = {}
    network_view = 'default'
    network = None

    def __init__(self, uid, default, name, viewtype='networkview', network=None):
        self.uid = uid
        self.default = default
        self.name = name
        self.viewtype = viewtype
        self.network = network

    @property
    def _ref(self):
        '''
        (ansidev) jtanner-OSX:AP-NIOS_FLASK_MOCK jtanner$ curl -k -u admin:infoblox 'https://192.168.10.10/wapi/v2.1/network'
        [
            {
                "_ref": "network/ZG5zLm5ldHdvcmskMS4wLjAuMC8yNC8w:1.0.0.0/24/default",
                "network": "1.0.0.0/24",
                "network_view": "default"
            },
            {
                "_ref": "network/ZG5zLm5ldHdvcmskMi4wLjAuMC8yNC8x:2.0.0.0/24/ansible-view",
                "network": "2.0.0.0/24",
                "network_view": "ansible-view"
            }
        ]
        (ansidev) jtanner-OSX:AP-NIOS_FLASK_MOCK jtanner$ curl -k -u admin:infoblox 'https://192.168.10.10/wapi/v2.1/ipv6network'
        [
            {
                "_ref": "ipv6network/ZG5zLm5ldHdvcmskZmU4MDo6LzY0LzA:fe80%3A%3A/64/default",
                "comment": "this is a test comment",
                "network": "fe80::/64",
                "network_view": "default"
            }
        ]
        '''
        # <WAPITYPE>/<REFDATA>:<NAME>[/<NAMEN>]
        out = self.viewtype
        out += '/'
        out += self.uid
        out += ':'
        out += self.name
        out += '/'
        out += str(self.default).lower()
        return out
        #return self.viewtype + '/' + self.uid + ':' + self.name + '/' + str(self.default).lower()

    def to_dict(self):
        ddict = {
            '_ref': self._ref,
            'is_default': self.default,
            'name': self.name,
            'comment': self.comment,
            'extattrs': self.extattrs,
            'network_view': self.network_view
        }
        return ddict


class DataModel(object):
    def __init__(self):
        self.views = {
            'network': [NetworkView('ZG5zLm5ldHdvcmtfdmlldyQw', True, 'default', network='1.0.0.0/24')],
            'ipv6network': [NetworkView('ZG5zLm5ldHdvcmskZmU4MDo6LzY0LzA', True, 'default', network='fe80::/64')],
            'zone_auth': [],
            'view': [],
            'record:host': []
        }

    def create_view(self, payload, viewtype='view'):
        # '{"name": "ansible-dns", "network_view": "default"}'
        # res = DATA.create_view(request.get_json())
        view = NetworkView(
            'XXXXXX',
            False,
            payload.get('name', ''),
            viewtype=viewtype
        )
        if payload.get('network'):
            view.network = payload['network']
        if payload.get('network_view'):
            view.network_view = payload['network_view']
        self.views[viewtype].append(view)
        return view

    def delete_view_by_refid(self, refid):
        for k,v in self.views.items():
            for idx,x in enumerate(v):
                if x._ref == refid:
                    print('REMOVING %s' % x._ref)
                    self.views[k].remove(x)
                    break

    def update_view_by_refid(self, refid, params):
        for k,v in self.views.items():
            for idx,x in enumerate(v):
                if x._ref == refid:
                    for pk,pv in params.items():
                        print('setting %s to %s on %s' % (pk, pv, refid))
                        setattr(self.views[k][idx], pk, pv)
                    break

    def serialize_views(self, name=None):
        res = []
        for k,v in self.views.items():
            if name:
                res += [x.to_dict() for x in v if x.name == name]
            else:
                res += [x.to_dict() for x in v]
        return res

    def serialize_view(self, view_type):
        print('serializing %s view' % view_type)
        res = [x.to_dict() for x in self.views[view_type]]
        return res

    def serialize_view_by_refid(self, refid):
        view = None
        for k,v in self.views.items():
            for x in v:
                if x._ref == refid:
                    view = x
                    break
        if view:
            return view.to_dict()
        return view


DATA = DataModel()


@app.route('/wapi/v2.1/<viewtype>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def v21_base(viewtype):
    if viewtype != 'view':
        viewtype = viewtype.replace('view', '')
    print('VIEWTYPE: %s METHOD: %s' % (viewtype, request.method))
    args = request.args.to_dict()
    pprint(args)

    if request.method == 'GET':
        return jsonify(DATA.serialize_view(viewtype))
        #return jsonify({})
    elif request.method == 'POST':
        view = DATA.create_view(request.get_json())
        print('# CREATED ...')
        pprint(DATA.serialize_views())
        payload = '"%s"' % view._ref
        return payload, 201

    return jsonify({})


@app.route('/wapi/v2.1/<viewtype>/<refid>/<subname>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def v21_abstractview_ref(viewtype, refid, subname):
    _refid = 'view/' + refid + '/' + subname
    if viewtype != 'view':
        viewtype = viewtype.replace('view', '')
    print('VIEWTYPE: %s METHOD: %s REFID: %s' % (viewtype, request.method, _refid))
    args = request.args.to_dict()
    pprint(args)

    if request.method == 'GET':
        return jsonify(DATA.serialize_view_by_refid(_refid))
    elif request.method == 'POST':
        view = DATA.create_view(request.get_json(), viewtype=viewtype)
        return jsonify(view.to_dict()), 201
    elif request.method == 'PUT':
        DATA.update_view_by_refid(_refid, request.get_json())
        pprint(DATA.serialize_view_by_refid(_refid))
        return jsonify(DATA.serialize_view_by_refid(_refid))
    elif request.method == 'DELETE':
        print('deleting %s' % _refid)
        DATA.delete_view_by_refid(_refid)
        pprint(DATA.serialize_views())
        return jsonify({})

    print('default return ...')
    return ''

    return jsonify({})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443, ssl_context='adhoc')
