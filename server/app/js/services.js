'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
var MyAppServices = angular.module('MyAppServices', []);

MyAppServices.service('DataService',['$http',function($http){
	var that = this;
	this.all_data = {};
	this.all_types = [];

	this.loadData = function(callback){
		$http.get("json/data.json").success(function(data){
			var parse_rcs = parseData(data);
			that.all_data = parse_rcs[0];
			that.all_types = parse_rcs[1]; //store all of type in system
			if(data.length>0){
				that.end_month = data[0].endMonth;
				that.start_month = data[0].startMonth;
			}
			that.month_list = getMonths(data);
			callback();
		});	
	}

	this.getCurrentData = function(date_type,date_month){
		var values = this.all_data[date_type];
		var rc = [];
		for(var i=0;i<values.length;i++){
			if(values[i].month == date_month.toString()){
				var val = values[i];
				rc = [val['me-1'],val['me'],val['me+1']];
				break;
			}
		}
		return rc;
	}

	this.getHistoryData = function(data_type,me_type){
		var real_list = compositeList(this.all_data[data_type+"_real"],me_type);
		var predict_list = compositeList(this.all_data[data_type+"_predict"],me_type);

		return [predict_list,real_list];
	}
}]);

function getMonths(all_datas){
	var month_list = [];
	if(all_datas.length>0){
		var smaple = all_datas[0].values;
		for(var i=0;i<smaple.length;i++){
			var dict = smaple[i];
			month_list.push(dict.month);
		}	
		month_list.sort();
	}
	return month_list;
}


function compositeList(dicts,me_type){
	var data_list = [];
	for(var i=0;i<dicts.length;i++){
		var dict = dicts[i];
		data_list.push(dict[me_type]);
	}
	return data_list;
}


function parseData(data_obj){
	var rc_data = {};
	var pre_types = [];
	for(var i=0;i<data_obj.length;i++){
		var data_type = data_obj[i].type;
		var pre_type = getIsPredict(data_obj[i].isPredict);
		rc_data[data_type+"_"+pre_type] = data_obj[i].values;
		pre_types.push(data_type+"_"+pre_type);
	}
	return [rc_data,pre_types];
}

function getIsPredict(bool){
	return bool?"predict":"real";
}
