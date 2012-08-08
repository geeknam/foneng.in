define([
    'underscore', 'backbone', 'models/message'], function(_, Backbone, Message){
  
    var MessagesCollection = Backbone.Collection.extend({

    model: Message,
    url: '/account/conversations/'

    });
    
    return MessagesCollection;
});
