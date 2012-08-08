define([
    'jquery', 'underscore', 'backbone', 'collections/messages', 'views/messages',
    'text!templates/app.html'
    ], function($, _, Backbone, MessagesCollection, MessageView, appTemplate){
    
        var AppView = Backbone.View.extend({

        el: $("#message-app"),

        appTemplate: _.template(appTemplate),

        initialize: function() {
            _.bindAll(this, 'addOne', 'addAll', 'render');

            this.Messages = new MessagesCollection();

            this.Messages.bind('add', this.addOne);
            this.Messages.bind('reset', this.addAll);
            this.Messages.bind('all', this.render);

            this.Messages.fetch();
        },

        render: function() {
        
        },

        addOne: function(message) {
            var view = new MessageView({model: message});
            this.$("#message-list").append(view.render().el);
        },

        addAll: function() {
            this.Messages.each(this.addOne);
        }

    });

    return AppView;

});
