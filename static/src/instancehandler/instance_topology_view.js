//GraphEditor instance
var graph_editor = new TCD3.ModelGraphEditor();

var type_view = {
    "nsr": ["vnfr", "ns_vl"],
    "vnfr": ["vdur", "cp", "vnf_vl"]
};

var params = {
    node: {
        type: type_view['nsr'],
        group: []
    },
    link: {
        group: [],
        view: ['nsr']
    }
};

$(document).ready(function () {

    graph_editor.addListener("filters_changed", changeFilter);
    graph_editor.addListener("node:selected", refreshElementInfo);
    graph_editor.addListener("node:deselected", refreshElementInfo);

    // graph_editor initialization
    graph_editor.init({
        width: $('#graph_editor_container').width(),
        height: $('#graph_editor_container').height(),
        data_url: window.location.href,
        //desc_id: getUrlParameter('id'),
        gui_properties: osm_gui_properties,
        edit_mode: false,
        behaviorsOnEvents: {
            viewBased: false,
            behaviors: buildBehaviorsOnEvents()
        }
    });
    graph_editor.handleFiltersParams(params);

});



function handleForce(el) {
    graph_editor.handleForce((el.getAttribute('aria-pressed') === "true"));
}

function changeFilter(e, c) {
    if (c && c.link && c.link.view[0]) {
        updateLegend(c.link.view[0]);
    }
    layerDetails(graph_editor.getCurrentFilters())
}

function resetFilters() {
    graph_editor.handleFiltersParams(params);
}

function buildBehaviorsOnEvents() {
    var self = this;
    var contextmenuNodesAction = [
        {
            title: 'Explore',
            action: function (elm, c_node, i) {
                if (c_node.info.type !== undefined) {
                    var current_layer_nodes = Object.keys(graph_editor.model.layer[graph_editor.getCurrentView()].nodes);
                    if (current_layer_nodes.indexOf(c_node.info.type) >= 0) {
                        if (graph_editor.model.layer[graph_editor.getCurrentView()].nodes[c_node.info.type].expands) {
                            var new_layer = graph_editor.model.layer[graph_editor.getCurrentView()].nodes[c_node.info.type].expands;
                            graph_editor.handleFiltersParams({
                                node: {
                                    type: Object.keys(graph_editor.model.layer[new_layer].nodes),
                                    group: [c_node.id]
                                },
                                link: {
                                    group: [c_node.id],
                                    view: [new_layer]
                                }
                            });

                        }
                        else {
                            showAlert('This is not an explorable node.')
                        }
                    }
                }
            },
            edit_mode: false
        }];

    return {
        'nodes': contextmenuNodesAction
    };

}

function refreshElementInfo(event, element) {
    if (event.type === 'node:selected') {
        switch (element.info.type) {
            case 'vnfr':
                vnfrDetails(element.info.osm);
                break;
            case 'vdur':
                vdurDetails(element.info.osm);
                break;
            case 'int_cp':
            case 'cp':
                cpDetails(element.info.osm);
                break;
            case 'vnf_vl':
            case 'ns_vl':
                vlDetails(element.info.osm);
                break;
        }
    }
    else if (event.type === 'node:deselected') {
        layerDetails(graph_editor.getCurrentFilters())
    }
}

function layerDetails(filters) {
    var side = $('#side');
    var graph_parameters = graph_editor.getGraphParams();
    var layer_template = '';
    if(graph_parameters['view'] && filters.link.view.length >0 && filters.link.view[0]){
        if(filters.link.view[0] === 'nsr') {
            layer_template = getMainSection('NS View');
            layer_template += getChildrenTable(graph_parameters['view']['nsr']);
        }
        else if(filters.link.view[0] === 'vnfr') {
            layer_template = getMainSection('VNF View');
            var vnfr_id = filters.link.group[0];
            layer_template += getChildrenTable(graph_parameters['view']['vnfr'][vnfr_id]);
        }
    }

    side.empty();
    side.append(layer_template)
}

function updateLegend(view) {
    var legend = $('#legenda');
    var nodes = type_view[view];
    var legend_template = '';
    var nodes_properties = osm_gui_properties['nodes'];
    for (var n in nodes){
        var node = nodes[n];
        if(nodes_properties[node]){
            legend_template += '<div class="node">' +
                '<div class="icon" style="background-color:' + nodes_properties[node].color +'"></div>' +
                '<div class="name">' +nodes_properties[node].name + '</div></div>';
        }
    }

    legend.empty();
    legend.append(legend_template)

}

var map = {
    'ip-address': 'IP', 'vnfd-id': 'Vnfd Id', 'vnfd-ref': 'Vnfd Ref', 'vim-account-id': 'Vim Id',
    'member-vnf-index-ref': 'Member index', 'created-time': 'Created', 'id': 'Id', 'mgmt-network': 'Mgmt network',
    'name': 'Name', 'type': 'Type', 'vim-network-name': 'Vim network name', 'connection-point-id': 'Cp Id',
    'vdu-id-ref': 'Vdu Id', 'nsr-id-ref': 'Nsr Id'
};

function vnfrDetails(vnfr) {
    var side = $('#side');
    var vnfr_template = getMainSection('VNFR');

    vnfr_template += getChildrenTable(vnfr);
    side.empty();
    side.append(vnfr_template)
}

function vdurDetails(vdur) {
    var side = $('#side');
    var vdur_template = getMainSectionWithStatus('VDUR', vdur['status'] === 'ACTIVE');
    vdur_template += getChildrenTable(vdur);

    if (vdur['interfaces'].length > 0) {
        vdur_template += getSubSection('Interfaces:');
        vdur_template += '<table class="children">';

        for (var i = 0; i < vdur['interfaces'].length; ++i) {
            var interface = vdur['interfaces'][i];
            var interface_template = '<tr><td>' + interface['name'] + '</td>'
                + '<td>IP:' + interface['ip-address'] + '</td>'
                + '<td>MAC:' + interface['mac-address'] + '</td>';
            vdur_template += interface_template;
        }
        vdur_template += '</table>';
    }

    side.empty();
    side.append(vdur_template)
}

function cpDetails(cp) {
     var side = $('#side');
    var cp_template = getMainSection('Connection Point');

    cp_template += getChildrenTable(cp);
    side.empty();
    side.append(cp_template);
}

function vlDetails(vl) {
    var side = $('#side');
    var vl_template = getMainSection('Virtual Link');

    vl_template += getChildrenTable(vl);
    side.empty();
    side.append(vl_template);
}


function getMainSection(title) {
    return '<div class="section"><span style="font-weight: 500;">' + title + '</span></div>';
}

function getSubSection(title) {
    return '<div class="section"><span>' + title + '</span></div>';
}

function getMainSectionWithStatus(title, status) {
    var template = '<div class="section"><span style="font-weight: 500;">' + title + '</span>';
    if (status)
        template += '<div class="status active"><span class="indicator"></span> ACTIVE</div>';
    else
        template += '<div class="status"><span class="indicator"></span>NO ACTIVE</div>';
    template += '</div>';
    return template;
}

function getChildrenTable(data) {
    var template = '<table class="children">';

    for (var key in data) {
        if (typeof data[key] === 'string') {
            var key_map = (map[key]) ? map[key] : key;
            template += '<tr><td>' + key_map + '</td><td>' + data[key] + '</td></tr>';
        }
    }
    template += '</table>';
    return template;
}