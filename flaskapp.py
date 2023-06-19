#!/usr/bin/env python

# https://www.infoblox.com/wp-content/uploads/infoblox-deployment-infoblox-rest-api.pdf

import base64
import sys

import flask
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
    parent = None
    view = None
    viewtype = None
    _uid = None
    is_default = False
    name = None
    ptrdname = None
    comment = None
    extattrs = {}
    network_view = 'default'
    network = None
    options = []
    fqdn = None
    ipv4addrs = []
    ipv6addrs = []
    ipv4addr = None
    ipv6addr = None
    configure_for_dns = True
    ipv4 = None
    ipv6 = None
    canonical = None
    mail_exchanger = None
    preference = None
    port = None
    priority = None
    target = None
    weight = None
    order = None
    replacement = None
    text = None
    zone_format = None
    grid_primary = None
    grid_secondaries = None
    ns_group = None
    delegate_to = []
    forwarding_servers = []
    external_servers = []
    stub_members = []
    members = []
    master_candidate = False
    start_addr = None
    end_addr = None
    member = None

    def __init__(self, uid=None, isdefault=False, name=None, viewtype='network', network=None, comment=None):
        # `ZG5zLm5ldHdvcmskMS4wLjAuMC8yNC8w` == `dns.network$1.0.0.0/24/0`
        #self.uid = uid
        #self.uid = (base64.b64encode(str.encode(str(viewtype) + '$' + str(network) + '$' + str(name)))).decode('utf-8')
        if uid:
            self._uid = uid
        self.default = isdefault
        self.name = name
        self.viewtype = viewtype
        self.network = network
        self.comment = None

    @property
    def uid(self):

        # PARENT: ZG5zLnZpZXckLl9kZWZhdWx0 ==
        #   dns.view$._default
        # CHILD: ZG5zLnpvbmUkLl9kZWZhdWx0LmFuc2libGUtZG5z ==
        #   dns.zone$._default.ansible-dns

        '''
        $ for X in $(cat uuids.sorted.txt); do echo $X; echo $X | base64 -D ; echo ""; done;
        ZG5zLm5ldHdvcmskMTkyLjE2OC4xMC4wLzI0LzA
        dns.network$192.168.10.0/24
        ZG5zLm5ldHdvcmskZmU4MDo6LzY0LzA
        dns.network$fe80::/64
        ZG5zLm5ldHdvcmtfdmlldyQ0
        dns.network_view$4
        ZG5zLm5ldHdvcmtfdmlldyQw
        dns.network_view$0
        ZG5zLnZpZXckLjI5
        dns.view$.29
        ZG5zLnZpZXckLjMw
        dns.view$.30
        ZG5zLnZpZXckLl9kZWZhdWx0
        dns.view$._default
        ZG5zLnpvbmUkLl9kZWZhdWx0LmFuc2libGUtZG5z
        dns.zone$._default.ansible-dns
        '''

        if self._uid:
            return self._uid

        uid = 'dns.'

        if self.viewtype == 'zone_auth':
            uid += 'zone'
        else:
            try:
                uid += str.encode(self.viewtype)
            except:
                uid += self.viewtype

        uid += '$'

        if self.viewtype == 'zone_auth':
            uid += '._default.'

        if self.network is None:
            uid += 'None'
        else:
            try:
                uid += str.encode(self.network)
            except:
                uid += self.network
        uid = str.encode(uid)
        uid = base64.b64encode(uid)
        uid = uid.decode('utf-8')

        '''
        uid = (base64.b64encode(
            'dns.' +
            str.encode(
                str(self.viewtype) +
                '$' +
                str(self.network)
            )
        )).decode('utf-8')
        '''
        return uid

    @property
    def ref(self):
        return self._ref

    @property
    def _refid(self):
        return self._ref

    @property
    def _ref(self):
        '''
        (ansidev) jtanner-OSX:AP-NIOS_FLASK_MOCK jtanner$ curl -k -u admin:infoblox 'https://192.168.10.10/wapi/v2.9/network'
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
        (ansidev) jtanner-OSX:AP-NIOS_FLASK_MOCK jtanner$ curl -k -u admin:infoblox 'https://192.168.10.10/wapi/v2.9/ipv6network'
        [
            {
                "_ref": "ipv6network/ZG5zLm5ldHdvcmskZmU4MDo6LzY0LzA:fe80%3A%3A/64/default",
                "comment": "this is a test comment",
                "network": "fe80::/64",
                "network_view": "default"
            }
        ]

        network/ZG5zLm5ldHdvcmskMTkyLjE2OC4xMC4wLzI0LzA:192.168.10.0/24/default
        '''
        # <WAPITYPE>/<REFDATA>:<NAME>[/<NAMEN>]
        if self.viewtype == 'network':
            out = self.viewtype
            out += '/'
            out += self.uid
            out += ':'
            out += str(self.network)
            out += '/'
            out += self.network_view
        else:
            out = self.viewtype
            out += '/'
            out += self.uid
            out += ':'
            out += self.name if self.ptrdname is None else self.get_ptr_name()
            out += '/'
            out += str(self.default).lower()
        return out
        #return self.viewtype + '/' + self.uid + ':' + self.name + '/' + str(self.default).lower()

    def to_dict(self, fields=[]):
        ddict = {
            'uid': self.uid,
            '_ref': self._ref,
            #'_ref': self.uid,
            'is_default': self.default,
            'name': self.name,
            'ptrdname': self.ptrdname,
            'comment': self.comment,
            'extattrs': self.extattrs,
            'network_view': self.network_view,
            'network': self.network,
            'view': self.view,
            'viewtype': self.viewtype,
            'options': self.options,
            'fqdn': self.fqdn,
            'ipv4addrs': self.ipv4addrs,
            'ipv6addrs': self.ipv6addrs,
            'ipv4addr': self.ipv4addr,
            'ipv6addr': self.ipv6addr,
            'configure_for_dns': self.configure_for_dns,
            'ipv4': self.ipv4,
            'ipv6': self.ipv6,
            'canonical': self.canonical,
            'mail_exchanger': self.mail_exchanger,
            'preference': self.preference,
            'port': self.port,
            'priority': self.priority,
            'target': self.target,
            'weight': self.weight,
            'order': self.order,
            'replacement': self.replacement,
            'text': self.text,
            'zone_format': self.zone_format,
            'grid_primary': self.grid_primary,
            'grid_secondaries': self.grid_secondaries,
            'ns_group': self.ns_group,
            'delegate_to': self.delegate_to,
            'forwarding_servers': self.forwarding_servers,
            'external_servers': self.external_servers,
            'stub_members': self.stub_members,
            'members': self.members,
            'master_candidate': self.master_candidate,
            'start_addr': self.start_addr,
            'end_addr': self.end_addr,
            'member': self.member,
        }
        if fields:
            for x in fields:
                if x not in ddict:
                    if not hasattr(self, x):
                        ddict[x] = None
                    else:
                        ddict[x] = getattr(self, x)
        return ddict

    def get_ptr_name(self):
        """Get the name in the _ref for PTR:RECORD

        :return: str
        """
        pget = self.ipv6addr if self.ipv4addr is None else self.ipv4addr
        return "%s.in-addr.arpa" % '.'.join(reversed(str(pget).split('.')))


class DataModel(object):
    def __init__(self):
        self.views = {
            'network': [NetworkView(uid='ZG5zLm5ldHdvcmtfdmlldyQw', isdefault=True, name='default', network='1.0.0.0/24')],
            'networkview': [NetworkView(uid='ZG5zLm5ldHdvcmtfdmlldyQw', isdefault=True, name='default', network='1.0.0.0/24')],
            'ipv6network': [NetworkView(uid='ZG5zLm5ldHdvcmskZmU4MDo6LzY0LzA', isdefault=True, name='default', network='fe80::/64')],
            'zone_auth': [],
            'fixedaddress': [],
            'view': [NetworkView(isdefault=True, name='default', viewtype='view')],
            'record:host': [],
            'record:ptr': [],
            'record:a': [],
            'record:aaaa': [],
            'record:cname': [],
            'record:mx': [],
            'record:srv': [],
            'record:naptr': [],
            'record:txt': [],
            'nsgroup:delegation': [],
            'nsgroup:forwardingmember': [],
            'nsgroup:forwardstubserver': [],
            'nsgroup:stubmember': [],
            'range': [],
        }
        # ZG5zLm5ldHdvcmtfdmlldyQw == dns.network_view$0
        # ZG5zLm5ldHdvcmskZmU4MDo6LzY0LzA == dns.network$fe80::/64

    def create_view(self, payload, viewtype='view', parent=None):
        # '{"name": "ansible-dns", "network_view": "default"}'
        # res = DATA.create_view(request.get_json())
        print ('########### VIEWTYPE: ' + viewtype)
        view = NetworkView(
            uid=None,
            isdefault=False,
            name=payload.get('name', ''),
            viewtype=viewtype
        )
        '''
        if payload.get('network'):
            view.network = payload['network']
        if payload.get('network_view'):
            view.network_view = payload['network_view']
        if payload.get('comment'):
            view.comment = payload['comment']
        '''
        if parent:
            view.parent = parent
        for k,v in payload.items():
            setattr(view, k, v)
        self.views[viewtype].append(view)
        return view

    def delete_view_by_refid(self, refid, viewtype=None):
        for k,v in self.views.items():
            if viewtype and viewtype != k:
                continue
            for idx,x in enumerate(v):
                if x._ref == refid:
                    print('REMOVING %s' % x._ref)
                    self.views[k].remove(x)
                    #break

    def update_view_by_refid(self, refid, params):
        print('# UPDATING REFID %s' % refid)
        #refid = refid.replace('view', 'networkview')
        viewk = None
        viewix = None
        changed = False
        for k,v in self.views.items():
            for idx,x in enumerate(v):
                if x._refid != refid:
                    print('# %s != %s' % (x._refid, refid))
                else:
                    print('# %s == %s' % (x._refid, refid))
                if x._ref == refid:
                    viewk = k
                    viewix = idx
                    for pk,pv in params.items():
                        print('# pk: %s pv: %s' % (pk, pv))
                        if pk == 'options':
                            # INPUT ...
                            # options: [
                            #   {'name': 'domain-name',
                            #    'use_option: True,
                            #    'value': 'ansible.com',
                            #    'vendor_class': 'DHCP'}
                            # ]
                            # RESULT ...
                            # u'options': [{u'name': u'dhcp-lease-time',
                            # u'num': 51, u'use_option': False, u'value':
                            # u'43200', u'vendor_class': u'DHCP'}]
                            opts = x.options[:]
                            if not opts:
                                opts = pv[:]
                            else:
                                for idr,reqopt in enumerate(pv):
                                    isset = False
                                    for idv,viewopt in enumerate(opts):
                                        if viewopt.get('name') != reqopt.get('name'):
                                            continue
                                        for rk,rv in reqopt.items():
                                            opts[idv][rk] = rv
                                        isset = False
                                    if not isset:
                                        opts.append(reqopt)

                            setattr(self.views[k][idx], pk, opts[:])
                        else:
                            if getattr(self.views[k][idx], pk) != pv:
                                print('%s is "%s" on %s' % (pk, getattr(x, pk), refid))
                                print('setting %s to "%s" on %s' % (pk, pv, refid))
                                setattr(self.views[k][idx], pk, pv)
                                changed = True
                    break
        print('# %s updated? %s' % (refid, changed))
        print('# viewk: %s' % viewk)
        print('# viewix: %s' % viewix)
        if viewk is not None and viewix is not None:
            print('# accessing found view')
            thisview = self.views[viewk][viewix]
            print('# return %s' % thisview)
            return thisview
        else:
            return None

    '''
    def update_view_by_uid(self, uid, params):
        print('# UPDATING UID %s' % uid)
        viewk = None
        viewix = None
        changed = False
        for k,v in self.views.items():
            #print('# K: %s' % k)
            for idx,x in enumerate(v):
                print('# iteration %s' % x.uid)
                if x.uid != uid:
                    print('# %s != %s' % (x.uid, uid))
                if x.uid == uid:
                    viewk = k
                    viewix = idx
                    for pk,pv in params.items():
                        if getattr(self.views[k][idx], pk) != pv:
                            print('%s is "%s" on %s' % (pk, getattr(x, pk), uid))
                            print('setting %s to "%s" on %s' % (pk, pv, uid))
                            setattr(self.views[k][idx], pk, pv)
                            changed = True
                    break
        print('# %s updated? %s' % (uid, changed))
        if viewk and viewix:
            return self.views[viewk][viewix]
        else:
            return None
    '''

    def serialize_views(self, viewtype=None, name=None):
        res = []
        for k,v in self.views.items():
            if viewtype and viewtype != k:
                continue
            if name:
                print('# filtering all in %s by name %s' % (k, name))
                print([x for x in v])
                print([x.name for x in v])
                res += [x.to_dict() for x in v if x.name == name]
            else:
                print('# collecting all in %s' % k)
                res += [x.to_dict() for x in v]
        return res

    def serialize_view(self, view_type, name=None):
        #print('serializing %s view' % view_type)
        res = [x.to_dict() for x in self.views[view_type]]
        return res

    def serialize_view_by_refid(self, refid, returnfields=[]):
        view = None
        for k,v in self.views.items():
            for x in v:
                if x._ref == refid:
                    view = x
                    break
        if view:
            return view.to_dict(fields=returnfields)
        return view


DATA = DataModel()


@app.route('/wapi/v2.9/<viewtype>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def v21_base(viewtype):
    #if viewtype != 'view':
    #    viewtype = viewtype.replace('view', '')
    #print('VIEWTYPE: %s METHOD: %s' % (viewtype, request.method))

    print('# METHOD: %s VIEWTYPE: %s' % (
        request.method, viewtype
    ))
    args = request.args.to_dict()
    print('# REQARGS ...')
    pprint(args)
    print('# REQJSON ...')
    try:
        pprint(request.get_json())
    except:
        pprint({})

    if request.method == 'GET':
        print('# FETCHED VIEW ...')
        # payload = DATA.serialize_view(viewtype, name=args.get('name'))
        name = args.get('name', None)
        if name is None:
            name = args.get('ptrdname', None)
        payload = DATA.serialize_views(viewtype=viewtype, name=name)
        pprint(payload)
        return jsonify(payload)

    elif request.method == 'POST':
        print('# CREATE VIEWTYPE: %s' % viewtype)
        view = DATA.create_view(request.get_json(), viewtype=viewtype)
        print('# CREATED VIEW ...')
        pprint(view.to_dict())
        payload = '"%s"' % view._ref
        return payload, 201

    return jsonify({})

# /wapi/v2.9/network/bmV0d29yayQxLjAuMC4wLzI0JGRlZmF1bHQ%3D%3A1.0.0.0/24/default
# @app.route('/wapi/v2.9/<viewtype>/<refid>/<subname>', methods=['GET', 'POST', 'PUT', 'DELETE'])
# @app.route('/wapi/v2.9/<viewtype>/<refid>/<subname>/subsubname', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/wapi/v2.9/<viewtype>/<path:refpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def v21_abstractview_ref(viewtype, refid=None, subname=None, refpath=None, subsubname=None):

    '''
    _refid = 'view/' + refid + '/' + subname
    __refid = refid.split(':')[0]
    if viewtype != 'view':
        viewtype = viewtype.replace('view', '')

    print('VIEWTYPE: %s METHOD: %s REFID: %s _REFID: %s' % (
        viewtype, request.method, __refid, _refid
    ))
    '''

    print('# REFPATH: %s' % refpath)
    _refid = viewtype + '/' + refpath
    uid = refpath.split('/')[1].split(':')[0]
    print('# METHOD: %s VIEWTYPE: %s UID: %s _REFID: %s' % (
        request.method, viewtype, uid, _refid
    ))

    args = request.args.to_dict()
    print('# REQARGS ...')
    pprint(args)
    print('# REQJSON ...')
    try:
        pprint(request.get_json())
    except:
        pprint({})

    if request.method == 'GET':
        view = DATA.serialize_view_by_refid(_refid, returnfields=args.get('_return_fields', []))
        print('# FETCHED VIEW [%s]...' % _refid)
        pprint(view)
        return jsonify(view)
    elif request.method == 'POST':
        print('# CREATE VIEWTYPE: %s' % viewtype)
        view = DATA.create_view(request.get_json(), viewtype=viewtype)
        print('# CREATED VIEW [%s] ...' % view.to_dict()['_refid'])
        pprint(view.to_dict())
        return jsonify(view.to_dict()), 201
    elif request.method == 'PUT':
        view = DATA.update_view_by_refid(_refid, request.get_json())
        #view = DATA.update_view_by_uid(__refid, request.get_json())
        if not view:
            print('# ERROR!!! MODIFYING [%s] RETURN NO VIEW!' % _refid)
            return jsonify({})
        print('# MODIFIED VIEW [%s] ...' % view.uid)
        pprint(view.to_dict())
        return jsonify(view.to_dict()), 200
    elif request.method == 'DELETE':
        print('# DELETE VIEW [%s]' % _refid)
        DATA.delete_view_by_refid(_refid, viewtype=viewtype)
        pprint(DATA.serialize_views(viewtype=viewtype))
        return jsonify({})

    print('default return ...')
    #return ''
    return jsonify({})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443, ssl_context='adhoc')
