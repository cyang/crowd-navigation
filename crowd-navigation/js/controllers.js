'use strict';

app.controller("CrowdeeRoomCtrl", function ($scope, $location) {
	$scope.location = $location.path()
	
	$scope.user_id = null;
	$scope.user_weight = null;
	$scope.user_direction = "Nothing";
	$scope.aggregate_direction = "Nothing";
	$scope.room_key = null;
	$scope.crowd = [];
	
	Room.enter({}, function(crowdee_data)
	    {
			//Extract the data to scope variables.
			$scope.room_key = crowdee_data.room_key;
			$scope.user_id = crowdee_data.user_id;
			$scope.user_weight = crowdee_data.user_weight;
			$scope.tokbox_api_key = crowdee_data.tokbox_api_key;
			$scope.tokbox_session_id = crowdee_data.tokbox_session_id;
			$scope.tokbox_token = crowdee_data.tokbox_token;
			$scope.channel_token = crowdee_data.channel_token;
			
			
	    }
    );
	
	$scope.keyDown = function($event)
    {
        //Check if the key was an arrow key.
        if($event.keyCode == '37')
        {
            //Left arrow.
        	$scope.user_direction = "Left";
        }
        else if($event.keyCode == '38')
        {
            //Up arrow.
        	$scope.user_direction = "Forward";
        }
        else if($event.keyCode == '39')
        {
            //Right arrow.
        	$scope.user_direction = "Right";
        }
        else if($event.keyCode == '40')
        {
            //Down arrow.
        	$scope.user_direction = "Stop";
        }
        //local.direction = d;
        //crowd[local.current_user_id] = {"direction": local.direction, "weight": local.weight}
        //updateRoom();
        //sendMessage('/direction', 'd=' + d);
    };
});

app.controller("HostRoomCtrl", function ($scope) {
	
});
