if (typeof TCD3 === 'undefined') {
    var TCD3 = {};
}

TCD3.OsmController = (function (global) {
    'use strict';

    var DEBUG = true;

    OsmController.prototype.constructor = OsmController;

    /**
     * Constructor
     */
    function OsmController() {


    }


    OsmController.prototype.addNode = function (graph_editor, node, success, error) {
        log('addNode');
        var element_type = node.info.type;
        var desc_id = node.info.desc_id;
        var desc_type = node.info.desc_type;
        var data_form = new FormData();
        data_form.append('csrfmiddlewaretoken', getCookie('csrftoken'));
        for (var key in node) {
            data_form.append(key, node[key]);
        }
        $.ajax({
            url: '/projects/descriptors/' + desc_type + '/' + desc_id + '/addElement/' + element_type,
            type: 'POST',
            data: data_form,
            cache: false,
            contentType: false,
            processData: false,
            success: success,
            error: error
        });
    };

    OsmController.prototype.addLink = function (graph_editor, link, success, error) {
        log('addLink');

        var data_to_send = {
            'desc_id': link.desc_id,
            'source': link.source.id,
            'source_type': link.source.info.type,
            'target': link.target.id,
            'target_type': link.target.info.type,
            'view': link.view,
            'group': link.group
        };

        var desc_id = getUrlParameter('id');
        var desc_type = getUrlParameter('type');
        if (desc_type === 'nsd') {
            var element_type = 'cp';
            var data_form = new FormData();

            var vnfd_node = (link.source.info.type === 'vnf') ? link.source : link.target;
            var vld_node = (link.source.info.type === 'ns_vl') ? link.source : link.target;

            data_form.append('csrfmiddlewaretoken', getCookie('csrftoken'));
            data_form.append('vnfd-connection-point-ref', 'cp_temp');
            data_form.append('member-vnf-index-ref', vnfd_node.info.osm['member-vnf-index']);
            data_form.append('vnfd-id-ref', vnfd_node.info.osm['vnfd-id-ref']);
            data_form.append('vld_id', vld_node.info.osm['id']);

            $.ajax({
                url: '/projects/descriptors/' + desc_type + '/' + desc_id + '/addElement/' + element_type,
                type: 'POST',
                data: data_form,
                cache: false,
                contentType: false,
                processData: false,
                success: success,
                error: error
            });
        }

    };

    OsmController.prototype.removeNode = function (graph_editor, node, success, error) {
        log('removeNode');
        var desc_id = getUrlParameter('id');
        var desc_type = getUrlParameter('type');
        var element_type = node['info']['type'];
        var data_form = new FormData();
        data_form.append('csrfmiddlewaretoken', getCookie('csrftoken'));
        for (var key in node.info.osm) {
            data_form.append(key, node.info.osm[key]);
        }

        $.ajax({
            url: '/projects/descriptors/' + desc_type + '/' + desc_id + '/removeElement/' + element_type,
            type: 'POST',
            data: data_form,
            cache: false,
            contentType: false,
            processData: false,
            success: success,
            error: error
        });

    };

    OsmController.prototype.updateNode = function (graph_editor, node, args, success, error) {
        log('updateNode');
        var desc_id = getUrlParameter('id');
        var desc_type = getUrlParameter('type');
        var element_type = node['info']['type'];
        console.log(args)
        var data_form = new FormData();
        data_form.append('csrfmiddlewaretoken', getCookie('csrftoken'));
        data_form.append('old', JSON.stringify( node.info.osm));
        data_form.append('update', JSON.stringify(args));
        /*for (var key in node.info.osm) {
            data_form.append(key, node.info.osm[key]);
        }
        */

        $.ajax({
            url: '/projects/descriptors/' + desc_type + '/' + desc_id + '/updateElement/' + element_type,
            type: 'POST',
            data: data_form,
            cache: false,
            contentType: false,
            processData: false,
            success: success,
            error: error
        });

    };

    OsmController.prototype.updateGraphParams = function(args, success, error){
        var desc_id = getUrlParameter('id');
        var desc_type = getUrlParameter('type');
        var data_form = new FormData();
        data_form.append('csrfmiddlewaretoken', getCookie('csrftoken'));
        data_form.append('update', JSON.stringify(args));
        $.ajax({
            url: '/projects/descriptors/' + desc_type + '/' + desc_id + '/updateElement/graph_params',
            type: 'POST',
            data: data_form,
            cache: false,
            contentType: false,
            processData: false,
            success: success,
            error: error
        });
    };

    OsmController.prototype.removeLink = function (graph_editor, link, success, error) {
        log('removeLink');
        var data_to_send = {
            'desc_id': link.desc_id,
            'source': link.source.id,
            'source_type': link.source.info.type,
            'target': link.target.id,
            'target_type': link.target.info.type,
            'view': link.view,
            'group': link.group
        };

        var desc_id = getUrlParameter('id');
        var desc_type = getUrlParameter('type');

        if (desc_type === 'nsd') {
            var element_type = 'cp';
            var data_form = new FormData();

            var vnfd_node = (link.source.info.type === 'vnf') ? link.source : link.target;
            var vld_node = (link.source.info.type === 'ns_vl') ? link.source : link.target;

            data_form.append('csrfmiddlewaretoken', getCookie('csrftoken'));
            data_form.append('vnfd-connection-point-ref', 'cp_temp');
            data_form.append('member-vnf-index-ref', vnfd_node.info.osm['member-vnf-index']);
            data_form.append('vnfd-id-ref', vnfd_node.info.osm['vnfd-id-ref']);
            data_form.append('vld_id', vld_node.info.osm['id']);

            $.ajax({
                url: '/projects/descriptors/' + desc_type + '/' + desc_id + '/removeElement/' + element_type,
                type: 'POST',
                data: data_form,
                cache: false,
                contentType: false,
                processData: false,
                success: success,
                error: error
            });
        }
    };

    /**
     * Log utility
     */
    function log(text) {
        if (DEBUG)
            console.log("::OsmController::", text);
    }

    return OsmController;
}(this));

if (typeof module === 'object') {
    module.exports = TCD3.OsmController;
}