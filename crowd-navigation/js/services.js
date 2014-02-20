'use strict';

var services = angular.module('services', ['ngResource']);

services.factory('CrowdeeRoom', ['$resource',
    function($resource)
    {
		return $resource('/crowdee-room/:room_id', {}, {
	    	create: {method: 'POST'},
			enter: {method: 'PUT', params:{room_id:'@room_id'}}
	    });
    }
]);

services.factory('Channel', [
	function(){
		return{
			open: function(token){
				var channel = new goog.appengine.Channel(token);
		        var handler = {
		            'onopen': function() {},//onOpened,
		            'onmessage': function() {},//onMessage,
		            'onerror': function() {},
		            'onclose': function() {}
		        };
		        var socket = channel.open(handler);
		        //socket.onopen = onOpened;
		        //socket.onmessage = onMessage;
			}
		}
	}
]);