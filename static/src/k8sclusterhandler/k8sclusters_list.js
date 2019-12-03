/*
   Copyright 2019 EveryUP srl

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an  BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

function openModalRegisterK8s(args) {
    // load vim account list
    select2_groups = $('#k8sc_vim_account').select2({
        placeholder: 'Select VIM',
        width: '100%',
        ajax: {
            url: args.vim_list_url,
            dataType: 'json',
            processResults: function (data) {
                vims = [];
                if (data['datacenters']) {
                    for (d in data['datacenters']) {
                        var datacenter = data['datacenters'][d];
                        vims.push({ id: datacenter['_id'], text: datacenter['name'] })
                    }
                }

                return {
                    results: vims
                };
            }
        }
    });


    $('#modal_new_k8sc').modal('show');
}

function showK8sc(k8sc_id, k8sc_name) {
    var url_info = '/k8scluster/' + k8sc_id;
    var dialog = bootbox.dialog({
        message: '<div class="text-center"><i class="fa fa-spin fa-spinner"></i> Loading...</div>',
        closeButton: true
    });
    $.ajax({
        url: url_info,
        type: 'GET',
        dataType: "json",
        contentType: "application/json;charset=utf-8",
        success: function (result) {

            if (result['data'] !== undefined) {
                editorJSON.setValue(JSON.stringify(result['data'], null, "\t"));
                editorJSON.setOption("autoRefresh", true);
                dialog.modal('hide');
                $('#modal_show_k8sc').modal('show');
            }
            else {
                dialog.modal('hide');
                bootbox.alert("An error occurred while retrieving the information.");
            }
        },
        error: function (result) {
            dialog.modal('hide');
            bootbox.alert("An error occurred while retrieving the information.");
        }
    });
}

function deleteK8sc(k8sc_id, k8sc_name) {
    var url = "/k8scluster/"+k8sc_id+"/delete";
    bootbox.confirm("Are you sure want to delete " + k8sc_name + "?", function (result) {
        if (result) {
            var dialog = bootbox.dialog({
                message: '<div class="text-center"><i class="fa fa-spin fa-spinner"></i> Loading...</div>',
                closeButton: true
            });
            $.ajax({
                url: url,
                type: 'GET',
                dataType: "json",
                contentType: "application/json;charset=utf-8",
                success: function (result) {
                    if (result['error'] == true) {
                        dialog.modal('hide');
                        bootbox.alert("An error occurred.");
                    }
                    else {
                        table.ajax.reload();
                        dialog.modal('hide');
                    }
                },
                error: function (error) {
                    dialog.modal('hide');
                    bootbox.alert("An error occurred.");
                }
            });
        }
    })
}

var editorJSON;

$(document).ready(function () {

    var json_editor_settings = {
        mode: "javascript",
        showCursorWhenSelecting: true,
        autofocus: true,
        lineNumbers: true,
        lineWrapping: true,
        foldGutter: true,
        gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
        autoCloseBrackets: true,
        matchBrackets: true,
        extraKeys: {
            "F11": function (cm) {
                cm.setOption("fullScreen", !cm.getOption("fullScreen"));
            },
            "Esc": function (cm) {
                if (cm.getOption("fullScreen")) cm.setOption("fullScreen", false);
            },
            "Ctrl-Q": function (cm) {
                cm.foldCode(cm.getCursor());
            }
        },
        theme: "neat",
        keyMap: "sublime"
    };
    var myJsonTextArea = document.getElementById("k8sc_view_json");
    editorJSON = CodeMirror(function (elt) {
        myJsonTextArea.parentNode.replaceChild(elt, myJsonTextArea);
    }, json_editor_settings);

    $("#formCreatek8sc").submit(function (event) {
        event.preventDefault(); //prevent default action
        var post_url = $(this).attr("action"); //get form action url
        var request_method = $(this).attr("method"); //get form GET/POST method
        var form_data = new FormData(this); //Encode form elements for submission
        $.ajax({
            url: post_url,
            type: request_method,
            data: form_data,
            headers: {
                "Accept": 'application/json'
            },
            contentType: false,
            processData: false
        }).done(function (response, textStatus, jqXHR) {
            table.ajax.reload();
            $('#modal_new_k8sc').modal('hide');
        }).fail(function (result) {
            var data = result.responseJSON;
            var title = "Error " + (data.code ? data.code : 'unknown');
            var message = data.detail ? data.detail : 'No detail available.';
            bootbox.alert({
                title: title,
                message: message
            });
        });
    });

});