define([
    'underscore', 'backbone', 'models/message'], function(_, Backbone, Message){
  
    var MessagesCollection = Backbone.Collection.extend({

        model: Message,
        url: '/account/conversations/',

        incoming: function(){
            return this.filter(function(message){
                return message.get('type') == "incoming";
            });
        },

        outgoing: function(){
            return this.filter(function(message){
                return message.get('type') == 'outgoing';
            });
        }

    });
    
    return MessagesCollection;
});
