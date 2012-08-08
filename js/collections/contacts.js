define([
    'underscore', 'backbone', 'models/contact'], function(_, Backbone, Contact){
  
    var ContactsCollection = Backbone.Collection.extend({

        model: Contact,
        url: '/account/contacts'

    });
    
    return ContactsCollection;
});
