define(['jquery', 'underscore', 'backbone', 'models/contact', 'text!templates/contacts.html'
  ], function($, _, Backbone, Contact, contactsTemplate){
    
    var ContactView = Backbone.View.extend({
        model: Contact,
        tagName:  "li",

        template: _.template(contactsTemplate),

        initialize: function() {
            _.bindAll(this, 'render');
            this.render();
        },

        render: function() {
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        }

    });

    return ContactView;

});
