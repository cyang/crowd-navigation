'use strict';

var services = angular.module('services', ['ngResource']);

services.factory('Room', ['$resource',
    function($resource){
		return $resource('/room', {}, {
	    	create: {method: 'POST'},
			enter: {method: 'GET'}
	    });
    }
]);

services.factory('Channel', [
	function(){
		return{
			open: function(token){
				var channel = new goog.appengine.Channel(token);
		        var handler = {
		            'onopen': onOpened,
		            'onmessage': onMessage,
		            'onerror': function() {},
		            'onclose': function() {}
		        };
		        var socket = channel.open(handler);
		        socket.onopen = onOpened;
		        socket.onmessage = onMessage;
			}
		}
	}
]);