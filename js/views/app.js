define([
    'jquery', 'underscore', 'backbone',
    'collections/contacts', 'views/contacts',
    'collections/messages', 'views/messages',
    'text!templates/app.html'
    ], function($, _, Backbone, ContactsCollection, ContactView,
        MessagesCollection, MessageView,
        appTemplate){
    
        var AppView = Backbone.View.extend({

        el: $("#message-app"),

        appTemplate: _.template(appTemplate),

        initialize: function() {
            _.bindAll(this, 'addContact', 'addAllContacts',
            'addMessage', 'addAllMessages', 'render');

            this.Contacts = new ContactsCollection();
            this.Contacts.bind('add', this.addContact);
            this.Contacts.bind('reset', this.addAllContacts);
            this.Contacts.fetch();
        
            this.Messages = new MessagesCollection();
            this.Messages.bind('add', this.addMessage);
            this.Messages.bind('reset', this.addAllMessages);
            this.Messages.fetch();
        },

        render: function() {

        },

        addContact: function(contact) {
            var view = new ContactView({model: contact});
            this.$("#contact-list").append(view.render().el);
        },

        addAllContacts: function() {
            this.Contacts.each(this.addContact);
        },

        addMessage: function(message) {
            var view = new MessageView({model: message});
            this.$("#message-list").append(view.render().el);
        },

        addAllMessages: function() {
            this.Messages.each(this.addMessage);
        }

    });

    return AppView;

});
