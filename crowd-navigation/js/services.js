'use strict';

var services = angular.module('services', ['ngResource']);

services.factory('Room', ['$resource',
    function($resource)
    {
		return $resource('/room-resource', {}, {
	    	create: {method: 'POST'},
			enter: {method: 'PUT', params:{room_id: '@room_id'}},
	    	query: {method: 'GET', params:{query: 'true'}, isArray:true}
	    });
    }
]);

services.factory('Channel', ['$resource',
	function($resource)
	{
		var Channel = $resource('/channel/:command', {},
				{
					send: {method: 'POST', params:{command: '@command', room_id: '@room_id', direction: '@direction'}},
				}
		);
		/*Channel.open = function(token, onOpened, onMessage)
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
		};*/
		return Channel;
	}
]);