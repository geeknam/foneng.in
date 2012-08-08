
require.config({
    paths: {
        jquery: 'libs/jquery/jquery-min',
        underscore: 'libs/underscore/underscore',
        backbone: 'libs/backbone/backbone',
        text: 'libs/require/text'
    }
});

require(['views/app'], function(AppView){
    var app_view = new AppView();
});
