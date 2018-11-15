class OsmUtil():

    @staticmethod
    def remove_node(descriptor_type, descriptor, node_type, element_id, args):
        if descriptor_type == 'nsd':
            if 'nsd-catalog' in descriptor:
                nsd = descriptor['nsd-catalog']['nsd'][0]
            elif 'nsd:nsd-catalog' in descriptor:
                nsd = descriptor['nsd:nsd-catalog']['nsd'][0]

            if node_type == 'ns_vl':
                for k, v in enumerate(nsd['vld']):
                    if v['id'] == args['id']:
                        nsd['vld'].pop(k)
            elif node_type == 'vnf':
                for k, v in enumerate(nsd['constituent-vnfd']):
                    if str(v['member-vnf-index']) == str(args['member-vnf-index']) and str(v['vnfd-id-ref']) == str(
                            args['vnfd-id-ref']):
                        nsd['constituent-vnfd'].pop(k)
                        for j, vld in enumerate(nsd['vld']):
                            vld['vnfd-connection-point-ref'] = [item for item in vld['vnfd-connection-point-ref'] if
                                                                str(item['member-vnf-index-ref']) != str(
                                                                    args['member-vnf-index']) or str(
                                                                    item['vnfd-id-ref']) != str(args['vnfd-id-ref'])]
            elif node_type == 'cp':
                for vld in nsd['vld']:
                    if vld['id'] == args['vld_id']:
                        vld['vnfd-connection-point-ref'] = [item for item in vld['vnfd-connection-point-ref'] if
                                                            str(item['member-vnf-index-ref']) != str(
                                                                args['member-vnf-index-ref']) or str(
                                                                item['vnfd-id-ref']) != str(args['vnfd-id-ref'])]

        return descriptor

    @staticmethod
    def update_node(descriptor_type, descriptor, node_type, old, updated):
        if descriptor_type == 'nsd':
            if 'nsd-catalog' in descriptor:
                nsd = descriptor['nsd-catalog']['nsd'][0]
            elif 'nsd:nsd-catalog' in descriptor:
                nsd = descriptor['nsd:nsd-catalog']['nsd'][0]

            if node_type == 'ns_vl':
                for k, v in enumerate(nsd['vld']):
                    if v['id'] == old['id']:
                        nsd['vld'][k].update(updated)
                        print 'update here'
                        print old
            elif node_type == 'vnf':
                for k, v in enumerate(nsd['constituent-vnfd']):
                    if str(v['member-vnf-index']) == str(old['member-vnf-index']) and str(v['vnfd-id-ref']) == str(
                            old['vnfd-id-ref']):
                        print 'update here'
                        print old

        return descriptor

    @staticmethod
    def add_base_node(descriptor_type, descriptor, node_type, element_id, args):
        if descriptor_type == 'nsd':
            if 'nsd-catalog' in descriptor:
                nsd = descriptor['nsd-catalog']['nsd'][0]
            elif 'nsd:nsd-catalog' in descriptor:
                nsd = descriptor['nsd:nsd-catalog']['nsd'][0]
            if node_type == 'ns_vl':
                nsd['vld'].append({
                    "vim-network-name": "PUBLIC",
                    "name": element_id,
                    "vnfd-connection-point-ref": [],
                    "mgmt-network": "true",
                    "type": "ELAN",
                    "id": element_id
                })
            if node_type == 'vnf':
                indexes = []
                for cvnfd in nsd['constituent-vnfd']:
                    indexes.append(int(cvnfd["member-vnf-index"]))
                memberindex = max(indexes) + 1
                nsd['constituent-vnfd'].append({
                    "member-vnf-index": memberindex,
                    "vnfd-id-ref": element_id
                })
            if node_type == 'cp':
                for vld in nsd['vld']:
                    if vld['id'] == args['vld_id']:
                        if'vnfd-connection-point-ref' not in vld:
                            vld['vnfd-connection-point-ref'] = []
                        vld['vnfd-connection-point-ref'].append(
                            {
                                "vnfd-connection-point-ref": args['vnfd-connection-point-ref'],
                                "member-vnf-index-ref": args['member-vnf-index-ref'],
                                "vnfd-id-ref": args['vnfd-id-ref']
                            },
                        )
        return descriptor

    @staticmethod
    def update_graph_params(descriptor_type, descriptor, updated):
        if descriptor_type == 'nsd':
            if 'nsd-catalog' in descriptor:
                nsd = descriptor['nsd-catalog']['nsd'][0]
            elif 'nsd:nsd-catalog' in descriptor:
                nsd = descriptor['nsd:nsd-catalog']['nsd'][0]
            nsd.update(updated)

        return descriptor