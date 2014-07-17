$(document).ready(function(){

	var data = [{"mass":4031.30012839975,"possibility":0.63126694699516916},{"mass":4032.30640514565,"possibility":0.29041619348002851},{"mass":4033.31268189155,"possibility":0.066786706040476151},{"mass":4034.3189586374497,"possibility":0.010236685164203813},{"mass":4035.3252353833495,"possibility":0.0011764711739730327},{"mass":4036.3315121292489,"possibility":0.0001081395487056148},{"mass":4037.3377888751488,"possibility":8.2812877087660072E-06},{"mass":4038.3440656210487,"possibility":5.4344510440319318E-07},{"mass":4039.3503423669486,"possibility":3.1196996994207347E-08},{"mass":4040.3566191128484,"possibility":1.5915071766698441E-09},{"mass":4041.3628958587483,"possibility":7.305301023020394E-11},{"mass":4042.3691726046482,"possibility":3.0476571845879591E-12},{"mass":4043.375449350548,"possibility":1.1651898456422104E-13},{"mass":4044.3817260964479,"possibility":4.1110832900278207E-15},{"mass":4045.3880028423478,"possibility":1.3465493130954389E-16},{"mass":4046.3942795882476,"possibility":4.1154382062591695E-18},{"mass":4047.4005563341475,"possibility":1.1788870994998306E-19},{"mass":4048.4068330800474,"possibility":3.17753549603406E-21},{"mass":4049.4131098259472,"possibility":8.0867869042768843E-23},{"mass":4050.4193865718471,"possibility":1.9492674958017615E-24},{"mass":4051.425663317747,"possibility":4.4625326842110983E-26},{"mass":4052.4319400636468,"possibility":9.7273148772271723E-28},{"mass":4053.4382168095462,"possibility":2.0234478683666758E-29},{"mass":4054.4444935554461,"possibility":4.0251006967614467E-31},{"mass":4055.450770301346,"possibility":7.6712985708661925E-33},{"mass":4056.4570470472459,"possibility":1.4032111927043061E-34},{"mass":4057.4633237931457,"possibility":2.4673718880169507E-36},{"mass":4058.4696005390456,"possibility":4.1768271000892074E-38},{"mass":4059.4758772849455,"possibility":6.816396092319395E-40},{"mass":4060.4821540308453,"possibility":1.0737763832667142E-41},{"mass":4061.4884307767452,"possibility":1.6347082983359568E-43},{"mass":4062.4947075226451,"possibility":2.4077803579840131E-45},{"mass":4063.5009842685449,"possibility":3.4347550833859423E-47},{"mass":4064.5072610144448,"possibility":4.7500839555660187E-49},{"mass":4065.5135377603447,"possibility":6.3742978999908337E-51},{"mass":4066.5198145062445,"possibility":8.3073940051872108E-53},{"mass":4067.5260912521444,"possibility":1.0523332354096391E-54},{"mass":4068.5323679980443,"possibility":1.2966805471651902E-56},{"mass":4069.5386447439437,"possibility":1.5553253781232198E-58},{"mass":4070.5449214898435,"possibility":1.8172677089513569E-60},{"mass":4071.5511982357434,"possibility":2.0697197688808644E-62},{"mass":4072.5574749816433,"possibility":2.2991677768512784E-64},{"mass":4073.5637517275431,"possibility":2.4926118915192724E-66},{"mass":4074.570028473443,"possibility":2.6388201030626121E-68},{"mass":4075.5763052193429,"possibility":2.7294236155320532E-70},{"mass":4076.5825819652428,"possibility":2.7597039874033337E-72},{"mass":4077.5888587111426,"possibility":2.7289711492272069E-74},{"mass":4078.5951354570425,"possibility":2.6404961491105592E-76},{"mass":4079.6014122029424,"possibility":2.501030007836141E-78},{"mass":4080.6076889488422,"possibility":2.3199976527124505E-80},{"mass":4081.6139656947421,"possibility":2.1084939437529178E-82},{"mass":4082.620242440642,"possibility":1.8782226111880566E-84},{"mass":4083.6265191865418,"possibility":1.6405090922607788E-86},{"mass":4084.6327959324417,"possibility":1.4054898163632939E-88},{"mass":4085.6390726783416,"possibility":1.1815411644494328E-90},{"mass":4086.6453494242414,"possibility":9.7496951243121578E-93},{"mass":4087.6516261701413,"possibility":7.89946725216671E-95},{"mass":4088.6579029160412,"possibility":6.2864814837789394E-97},{"mass":4089.664179661941,"possibility":4.9153473277222418E-99},{"mass":4090.6704564078409,"possibility":3.77717065272053E-101},{"mass":4091.6767331537408,"possibility":2.8534454751842045E-103},{"mass":4092.6830098996406,"possibility":2.1197456474805464E-105},{"mass":4093.6892866455405,"possibility":1.5489087408341895E-107},{"mass":4094.6955633914404,"possibility":1.1135475841016627E-109},{"mass":4095.7018401373402,"possibility":7.8784722186793418E-112},{"mass":4096.70811688324,"possibility":5.4869566385719236E-114},{"mass":4097.71439362914,"possibility":3.762531256048628E-116},{"mass":4098.7206703750408,"possibility":2.5408993161810009E-118},{"mass":4099.7269471209411,"possibility":1.6902474022925662E-120},{"mass":4100.7332238668414,"possibility":1.1078028616314824E-122},{"mass":4101.7395006127417,"possibility":7.155092844869102E-125},{"mass":4102.745777358642,"possibility":4.5550931473155912E-127},{"mass":4103.7520541045424,"possibility":2.8588711482616881E-129},{"mass":4104.7583308504427,"possibility":1.7692572660825452E-131},{"mass":4105.764607596343,"possibility":1.0798612484343913E-133},{"mass":4106.7708843422433,"possibility":6.501368391440257E-136},{"mass":4107.7771610881437,"possibility":3.8617008820308333E-138},{"mass":4108.783437834044,"possibility":2.2634176177341351E-140},{"mass":4109.7897145799443,"possibility":1.309291005840885E-142},{"mass":4110.7959913258446,"possibility":7.4759169755713631E-145},{"mass":4111.8022680717449,"possibility":4.2142385162290689E-147},{"mass":4112.8085448176453,"possibility":2.3456755836996118E-149},{"mass":4113.8148215635456,"possibility":1.2893687657491097E-151},{"mass":4114.8210983094459,"possibility":7.0002132749311564E-154},{"mass":4115.8273750553462,"possibility":3.75433778546332E-156},{"mass":4116.8336518012466,"possibility":1.9893210993447213E-158},{"mass":4117.8399285471469,"possibility":1.0415640728363729E-160},{"mass":4118.8462052930472,"possibility":5.3893370705950683E-163},{"mass":4119.8524820389475,"possibility":2.7561973434699835E-165},{"mass":4120.8587587848479,"possibility":1.3933715420872007E-167},{"mass":4121.8650355307482,"possibility":6.9640203248579175E-170},{"mass":4122.8713122766485,"possibility":3.44146361345001E-172},{"mass":4123.8775890225488,"possibility":1.6817785626567182E-174},{"mass":4124.8838657684491,"possibility":8.1280844246462855E-177},{"mass":4125.8901425143495,"possibility":3.8855414887772685E-179},{"mass":4126.89641926025,"possibility":1.8374180202763966E-181},{"mass":4127.90269600615,"possibility":8.5961812426723108E-184},{"mass":4128.90897275205,"possibility":3.9791602124039719E-186},{"mass":4129.9152494979508,"possibility":1.8226852879269486E-188},{"mass":4130.92152624385,"possibility":8.2625013922203027E-191}];
	//alert(data);
	var possibility = 0;
	for(var i=0;i<data.length;i++){
		possibility = possibility +  data[i].possibility;
	}
	alert(possibility);
	// $.get(
 //    	"js/data.json",
 //    	function(data) {
 //    		var possibility = 0;
 //        	for(var i=0;i<data.length;i++){
 //        		possibility = possibility + data[i].possibility;
 //        	}
 //        	alert(possibility);
	// 	}
	// );
});