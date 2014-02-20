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
	function()
	{
		return {
			open: function(token, onOpened, onMessage)
			{
				var channel = new goog.appengine.Channel(token);
		        var handler = {
		            'onopen': onOpened,
		            'onmessage': onMessage,
		            'onerror': function(){},
		            'onclose': function(){}
		        };
		        var socket = channel.open(handler);
		        socket.onopen = onOpened;
		        socket.onmessage = onMessage;
			}
		}
	}
]);