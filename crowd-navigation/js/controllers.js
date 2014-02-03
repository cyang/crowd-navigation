'use strict';

app.controller("NavRoomCtrl", function ($scope) {
	$scope.user_id = "cat";
	$scope.user_weight = null;
	$scope.user_direction = "Nothing";
	$scope.room_key = null;
	$scope.crowd = [];
	
	$scope.keyDown = function(event)
    {
        //Check if the key was an arrow key.
        if(event.keyCode == '37')
        {
            //Left arrow.
            d = "Left";
        }
        else if(e.keyCode == '38')
        {
            //Up arrow.
            d = "Forward";
        }
        else if(e.keyCode == '39')
        {
            //Right arrow.
            d = "Right";
        }
        else if(e.keyCode == '40')
        {
            //Down arrow.
            d = "Stop";
        }
        $scope.user_direction = d;
        //local.direction = d;
        //crowd[local.current_user_id] = {"direction": local.direction, "weight": local.weight}
        //updateSource();
        //sendMessage('/direction', 'd=' + d);
    };
});
