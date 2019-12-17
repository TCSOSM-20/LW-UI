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

$(document).ready(function () {
    table = $('#vims_table').DataTable({
        responsive: true,
        "ajax": {
            "url": "/vims/list/",
            "dataSrc": function (json) {
                return json['datacenters'];
            },
            statusCode: {
                401: function () {
                    console.log("no auth");
                    moveToLogin(window.location.pathname);
                }
            },
            "error": function (hxr, error, thrown) {
                console.log(hxr)
                console.log(thrown)
                console.log(error);
            }

        },
        "columns": [
            {
                "render": function (data, type, row) {
                    return row["name"];
                },
                "targets": 0
            },
            {
                "render": function (data, type, row) {
                    return row['_id'];
                },
                "targets": 1
            },
            {
                "render": function (data, type, row) {
                    return row["vim_type"];
                },
                "targets": 2
            },
            {
                "render": function (data, type, row) {
                    return row["_admin"]['operationalState'];
                },
                "targets": 3
            },
            {
                "render": function (data, type, row) {
                    return row["_admin"]['description'] || '';
                },
                "targets": 4
            },
            {
                "render": function (data, type, row) {
                    return '<div class="btn-group"><button type="button" class="btn btn-default" ' +
                        'onclick="location.href=\'/vims/' + row['_id'] + '\'" data-toggle="tooltip" data-placement="top" data-container="body" title="Show Info">' +
                        '<i class="fa fa-info"></i>' +
                        '</button> ' +
                        '<button type="button" class="btn btn-default"' +
                        'onclick="javascript:deleteVim(\'' + row['_id'] + '\', \'' + row["name"] + '\')" data-toggle="tooltip" data-placement="top" data-container="body" title="Delete">' +
                        '<i class="far fa-trash-alt" ></i></button></div>';
                },
                "targets": 5,
                "orderable": false
            }
        ]
    });

    setInterval(function () {
        table.ajax.reload();
    }, 10000);

    $("#formCreateVIM").submit(function (event) {
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
            $('#modal_new_vim').modal('hide');
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

function openModalCreateVIM() {
    $('#modal_new_vim').modal('show');
}

function deleteVim(vim_id, vim_name) {
    var url = "/vims/" + vim_id + "/delete";
    bootbox.confirm("Are you sure want to delete " + vim_name + "?", function (result) {
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
                        dialog.modal('hide');
                        table.ajax.reload();
                    }
                },
                error: function (error) {
                    dialog.modal('hide');
                    var data = result.responseJSON;
                        var title = "Error " + (data && data.code ? data.code : 'unknown');
                        var message = data && data.detail ? data.detail : 'No detail available.';
                        bootbox.alert({
                            title: title,
                            message: message
                        });
                }
            });
        }
    })
}