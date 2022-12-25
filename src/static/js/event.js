/* global $, jQuery, _, common*/

$(function(){

    "use strict";

    const event ={


        render: function(){
            return [

                console.log(controller),
                edit_header.event_edit_header(controller.event, "event", [])
            ].join("\n");
        },



        name: "event",
        animation: "formtab",
        autofocus: "#eventtype",
        title: function() { return "controller.person.OWNERCODE" + ' - ' + "controller.person.OWNERNAME"; },
        routes: {
            "event": function() { common.module_loadandstart("event", "event?id=" + this.qs.id); }
        }
    }

    common.module_register(event);

});