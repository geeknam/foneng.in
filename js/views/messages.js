define(['jquery', 'underscore', 'backbone', 'models/todo', 'text!templates/messages.html'
  ], function($, _, Backbone, Message, messagesTemplate){
    
    var MessageView = Backbone.View.extend({
        model: Message,
        tagName:  "li",

        template: _.template(messagesTemplate),

        initialize: function() {
            _.bindAll(this, 'render');
            this.render();
        },

        render: function() {
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        }

    });

    return MessageView;

});
