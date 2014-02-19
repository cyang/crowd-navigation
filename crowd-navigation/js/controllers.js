'use strict';

app.controller("CrowdeeRoomCtrl", function ($scope, $location, Channel, CrowdeeRoom) {
	$scope.room_id = $location.path().split("/")[2];
	
	$scope.user_id = null;
	$scope.user_weight = null;
	$scope.user_direction = "Nothing";
	$scope.aggregate_direction = "Nothing";
	$scope.room_key = null;
	$scope.crowd = {};
    
    $scope.initialize = function()
    {
        Channel.open($scope.token);
        //document.onkeydown = changeDirection;
        //onMessage({data: '(( initial_message ))'});
    };
	
	CrowdeeRoom.enter({room_id: $scope.room_id}, function(crowdee_data)
	    {
			//Extract the data to scope variables.
			$scope.room_key = crowdee_data.room_key;
			$scope.user_id = crowdee_data.user_id;
			$scope.user_name = crowdee_data.user_name;
			$scope.user_weight = crowdee_data.user_weight;
			$scope.tokbox_api_key = crowdee_data.tokbox_api_key;
			$scope.tokbox_session_id = crowdee_data.tokbox_session_id;
			$scope.tokbox_token = crowdee_data.tokbox_token;
			$scope.channel_token = crowdee_data.channel_token;
			
			//Add the user to the crowd.
			$scope.crowd[$scope.user_id] = {"name": $scope.user_name, "weight": $scope.user_weight, "direction": $scope.user_direction};
			
			$scope.initialize();
			
			//TODO - Connect channel
	    }
    );
	
	/*Room.crowd({}, function(crowd)
	    {
			//Set the crowd.
			angular.forEach(crowd, function(crowdee, crowdee_id){
			    $scope.crowd[crowdee_id] = {"name": crowdee.name, "weight": $crowdee.weight, "direction": $crowdee.direction};
			});
	    }
    );*/
	
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
